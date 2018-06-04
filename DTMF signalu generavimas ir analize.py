
# coding: utf-8

# # DTMF signalų generavimas ir analizė

# # Audio ryšio sistemos modelis

# In[ ]:


get_ipython().run_line_magic('pylab', 'inline')


# In[ ]:


import scipy.constants as const
import scipy
import numpy as np
from scipy.io import wavfile
from IPython.core.display import HTML
from __future__ import division


# In[ ]:


duomenys = "Labas, pasauli"
ord('a')


# In[ ]:


def koduoti(duomenys):
    kodas=""
    for r in duomenys:
        k = format(ord(r), 'b').zfill(8)
        print r + '\t' + str(ord(r)) + '\t' + k
        kodas += k
    return kodas
#format(ord('a'), 'b').zfill(8)
kodas = koduoti(duomenys)


# In[ ]:


kodas


# In[ ]:


#amplitudine moduliacija
def moduliuoti(kodas):
    fs = 8000# diskretizavimo dažnis 8 kHz
    D = 0.1 # trukmė sek.
    f = 1000 # signalo dažnis Hz
    A1= 1 # amplitudė
    A0= 0.1
    t = linspace(0,D,num = fs*D)

    y0 = A0*sin(2*pi*f*t)
    y1 = A1*sin(2*pi*f*t)
    signalas = np.array([])
    for k in kodas:
        if k=='0':
            signalas=np.append(signalas, y0)
        if k=='1':
            signalas=np.append(signalas,y1)
    return signalas
signalas = moduliuoti(kodas)
plot(signalas)


# In[ ]:


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


# In[ ]:


fs=8000
# įrašomi duomenys į wav failus
wavfile.write('signalas2.wav', fs, (32768*signalas).astype(int16))

print 'signalas2.wav:'
wavGrotuvas("signalas2.wav")


# In[ ]:


fs, priimtas_signalas = wavfile.read('signalas2.wav')
plot(priimtas_signalas)
grid()


# In[ ]:


def demoduliuoti(priimtas_signalas):
    fs = 8000# diskretizavimo dažnis 8 kHz
    D = 0.1 # trukmė sek.
    f = 1000 # signalo dažnis Hz
    A1= 1 # amplitudė
    A0= 0.1
    t = linspace(0,D,num = fs*D)

    y0 = A0*sin(2*pi*f*t)
    y1 = A1*sin(2*pi*f*t)
    n = len(y0)
    c= []
    slenkstis = 10000
    for i in range (len(priimtas_signalas)//n):
        simb_std=std(priimtas_signalas[(i*n):(i+1)*n])
        c.append(simb_std)
    kodas = ""
    for ci in c:
        if ci>slenkstis:
            kodas += '1'
        else:
            kodas += '0'
    return kodas, c
demoduliuotas_signalas, std_kodas = demoduliuoti(priimtas_signalas)  


# In[ ]:


demoduliuotas_signalas


# In[ ]:


plot(std_kodas[:100])


# In[ ]:


def dekoduoti(kodas):
    duomenys = ""
    n = len(kodas)//8
    print n
    for i in range(n):
        raides_kodas = kodas[(i*8):((i+1)*8)]
        raides_kodas_10 = int(raides_kodas, 2)
        raide=chr(raides_kodas_10)
        print raides_kodas, raides_kodas_10, raide
        duomenys += raide
    return duomenys


# In[ ]:


duomenys = dekoduoti(demoduliuotas_signalas)


# In[ ]:


duomenys


# In[ ]:


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


# In[ ]:


# nubraižomas sugeneruotas signalas (k pirmųjų atskaitų)
k = 100
plot(t[:k],y1[:k],label='$f_1=697Hz$')
plot(t[:k],y2[:k],label='$f_2=1209Hz$')
xlabel('$t,s$')
ylabel('$y(t)$')
title('$y(t) = Asin(2{\pi}tf)$')
grid()
legend()


# In[ ]:


# apskaičiuojamas suminis dviejų dažnių signalas
yDTMF1 = (y1+y2)/2 
# nubraižomas sugeneruotas signalas (200 pirmųjų atskaitų)
plot(t[:k],y1[:k],label='$f_1=697Hz$')
plot(t[:k],y2[:k],label='$f_2=1209Hz$')
plot(t[:k],yDTMF1[:k],label='$DTMF1$')
xlabel('$t,s$')
ylabel('$y(t)$')
#title('$y(t) = Asin(2{\pi}tf)$')
grid()
legend()


# In[ ]:


# apskaičiuojamas ir nubraižomas DTMF1 signalo spektras
frq, Y = FFT(yDTMF1, fs)
plot(frq, abs(Y), 'r')
xlabel('$f, [Hz]$')
ylabel('$|Y(f)|$')
text(f1,-0.06,'$f_1$')
text(f2,-0.06,'$f_2$')
grid()
xlim(0,2000)


# In[ ]:


# nupaišoma DTMF1 signalo spektrograma
Pxx, freqs, bins, im = specgram(yDTMF1,NFFT = 2*1024, Fs=fs, noverlap=10);
xlabel('t, s')
ylabel('f, Hz')
#ylim(0,2000)


# In[ ]:


# nuskaitomi  ir nubraižomi duomenys iš wav failo
fs, x = wavfile.read('dtmf1.wav')
plot(x[:1000])
ylabel('$y(t)$')
grid()


# In[ ]:


# apskaičiuojamas ir nubraižomas spektras
frq, Y = FFT(x, fs)
plot(frq, abs(Y), 'r')
xlabel('$f, [Hz]$')
ylabel('$|Y(f)|$')
grid()
text(f1,-0.06,'$f_1$')
text(f2,-0.06,'$f_2$')
xlim(0,2000)


# In[ ]:


# nupaišoma signalo spektrograma
Pxx, freqs, bins, im = specgram(x,NFFT = 1024, Fs=fs, noverlap=100);
xlabel('t, s')
ylabel('f, Hz')
#ylim(0,2000)

