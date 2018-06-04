
# coding: utf-8

# # Audio ryšio sistemos modelis (AM)

# ## Duomenų perdavimo etapai:
# duomenys -> [kodavimas] -> [moduliavimas] -> [signalo perdavimas] -> [demoduliavimas] -> [dekodavimas] -> duomenys 

# In[1]:


get_ipython().run_line_magic('pylab', 'inline')
import scipy.constants as const
import scipy
import numpy as np
from scipy.io import wavfile
from scipy.signal import hilbert
from IPython.core.display import HTML
import pyaudio
import wave
from __future__ import division


# html 5 grotuvą atvaizduojanti funkcija,
# bus grojamas wav failas, kuris nurodomas failokelias kintamuoju

def wavGrotuvas(failokelias):
    src = """
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>wavGrotuvas</title>
    </head>
    
    <body>
    <audio controls="controls" style="width:300px" >
      <source src="files/%s" type="audio/wav" />
      Your browser does not support the audio element.
    </audio>
    </body>
    """%(failokelias)
    display(HTML(src))
    
# funkcija, kuri įrašo mikrofono priimamą garsą 
def wavImtuvas(failas,fs=44100,trukme=30):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = fs#8000# 44100
    CHUNK = 1024
    RECORD_SECONDS = trukme
    WAVE_OUTPUT_FILENAME = failas

    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    print ("įrašymas pradėtas")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        print ("."),
    print ("")
    print ("įrašymas baigtas")


    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    
# FFT funkcija, kuri skirta signalo spektrui apskaičiuoti
def FFT(y, fs):
    n = len(y)  # length of the signal
    k = np.arange(n)
    T = n / fs
    frq = k / T  # two sides frequency range
    frq = frq[range(n // 2)]  # one side frequency range
    Y = scipy.fft(y) / n  # fft computing and normalization
    Y = Y[range(n // 2)] / max(Y[range(n // 2)])
    return frq, Y

def Koduoti(duomenys, debug = False):
    kodas = ""
    for i in range(len(duomenys)):
        #kodas += "11111111"+"{0:b}".format(ord(duomenys[i])).zfill(8)+"00000000"
        kodas += "11111111"+"{0:b}".format(ord(duomenys[i])).zfill(8)+"00000000"
        if debug:
            print (s[i],"\t%03d\t"%ord(s[i]), "{0:b}".format(ord(s[i])).zfill(8))
    kodas += "1111111111111111"
    if debug:
        print (kodas)
    return kodas

def Moduliuoti(kodas,y0,y1):
    signalas = np.array([])
    for s in kodas:
        if s == '0':
            signalas = np.append(signalas,y0)
        if s == '1':
            signalas = np.append(signalas,y1)   
    return signalas

def Demoduliuoti(signalas,y0,y1):
    n = len(y0)
    c = []
    
    for i in range(len(signalas)//n):
        c.append(std((signalas[(i*n):((i+1)*n)])))
    kodas = ""
    for ci in c:
        if ci > mean(c):
            kodas+='1'
        else:
            kodas+='0'
    return kodas

def DemoduliuotiAM(signalas,y0,y1,sprendimo_lygis):
    n = len(y0)
    c = []
    
    for i in range(len(signalas)//n):
        c.append(std((signalas[(i*n):((i+1)*n)])))
    kodas = ""
    for ci in c:
        if ci > sprendimo_lygis:
            kodas+='1'
        else:
            kodas+='0'
    return kodas

def DemoduliuotiFM(signalas,y0,y1,fs=44100):
    ns = len(y0)
    c0 = []
    c1 = []
    indf0 = 50 #indeksas, kuris atitinka f0 
    indf1 = 200 #indeksas, kuris atitinka f1
    kodas = ""
    for i in range(len(priimtas_signalas)//ns):
        cs = priimtas_signalas[i*ns:(i+1)*ns]
        frq,Y = FFT(cs, fs)    

        yabs0 = abs(Y[indf0])
        yabs1 = abs(Y[indf1])
        c0.append(yabs0)
        c1.append(yabs1)
        if yabs1 > yabs0:
            kodas += "1"
        else:
            kodas += "0"
    return kodas
    
def Dekoduoti(kodas, debug = False):
    s = kodas.split('11111111')
    duomenys = ""
    for di in s:
        try:
            try:
                if debug:
                    print (di.replace('00000000',''), chr(int(di.replace('00000000',''),2)))
                duomenys += chr(int(di.replace('00000000',''),2))
            except:
                pass
        except ValueError:
            if debug:
                print ('_')
            duomenys += "_"
    return duomenys


# ## Pradiniai duomenys:

# In[ ]:


# sugeneruojamas sinusinis signalas
fs = 44100 # diskretizavimo dažnis 44,1 kHz
D = 0.05 # 1 bito trukmė sek.

f0 = 1000 # signalo dažnis Hz

A0 = 0.1 # amplitudė
A1 = 1.0

t = linspace(0,D,num = fs*D)

# loginiam 0 ir 1 naudojamos skirtingos amplitudės, tokiu būdu realizuojama AM
y0 = A0*sin(2*pi*f0*t) #loginio 0 signalas
y1 = A1*sin(2*pi*f0*t) #loginio 1 signalas

# įrašomi duomenys į wav failus
wavfile.write('y0.wav', fs, (32768*y0).astype(int16))
wavfile.write('y1.wav', fs, (32768*y1).astype(int16))

# sukuriami wavGrotuvai kiekvienam wav failui
print 'y0.wav:'
wavGrotuvas("y0.wav")
print 'y1.wav:'
wavGrotuvas("y1.wav")


# ## Siunčiami duomenys

# In[ ]:


siunciami_duomenys = " Amplitude modulation (AM) "
print ("Siunčiami duomenys:",siunciami_duomenys)


# ## Siunčiamų duomenų kodas

# In[ ]:


siunciamu_duomenu_kodas = Koduoti(siunciami_duomenys)
print ("Siunčiamų duomenų kodas:",siunciamu_duomenu_kodas)


# ## Siunčiamas signalas

# In[ ]:


signalas = Moduliuoti(siunciamu_duomenu_kodas,y0,y1)
trukme = D*len(siunciamu_duomenu_kodas)
print ("Signalo trukmė", trukme,"sek")
# įrašomi duomenys į wav failus
wavfile.write('signalas.wav', fs, (32768*signalas).astype(int16))
plot(signalas[:5000])


# ## Signalo siuntimas

# Nuspaudus grojimo mygtuką - bus girdimas sugeneruotas signalas. Tokiu būdu realizuojamas signalo siuntimas.

# In[ ]:


wavGrotuvas("signalas.wav")


# ## Signalo priėmimas

# Paleidus wavImtuvas() funkciją - pradedamas garso įrašymas iš mikrofono. Tokiu būdu realizuojamas signalo priėmimas.

# In[ ]:


wavImtuvas("priimtas_signalas.wav", fs, trukme*2)
fs, priimtas_signalas = wavfile.read("priimtas_signalas.wav")


# ## Signalo demoduliavimas

# In[ ]:


priimto_signalo_kodas = DemoduliuotiAM(priimtas_signalas,y0,y1,sprendimo_lygis=1800)
print ("Priimto signalo kodas:", priimto_signalo_kodas )


# In[ ]:


#surandama dalis kodo, kuriame yra naudinga informacija - užkoduoti duomenys
istart = priimto_signalo_kodas.find("11111111") # duomenų pradžios indeksas
iend = priimto_signalo_kodas.find("1111111111111111") # duomenų pabaigos indeksas
priimto_signalo_kodas = priimto_signalo_kodas[istart:iend+16]


# ## Signalo dekodavimas

# In[ ]:


priimti_duomenys = Dekoduoti(priimto_signalo_kodas, debug = True)
print "Priimti duomenys:", priimti_duomenys


# In[ ]:


#reikia parinkti sprendimo_lygį, kuris įrašomas į DemoduliuotiAM funkciją taip, kad tinkamai būtų atskirti loginiai 0 nuo 1

sprendimo_lygis = 2500

n = len(y0)
c = []
    
for i in range(len(priimtas_signalas)//n):
    c.append(std((priimtas_signalas[(i*n):((i+1)*n)])))
plot(c)
plot([0,len(c)],[sprendimo_lygis,sprendimo_lygis],'r-')

