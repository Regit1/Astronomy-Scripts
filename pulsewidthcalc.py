import numpy as np
from scipy.optimize import curve_fit
import random
import psrchive
import sys

with open("convergence.txt", "w") as file:
        pass
with open("failed_files.txt", "w") as f:
        pass

#Lets me import in file names
filename = sys.argv[1]
failcount = 0
#Try so script doesn't abort if an error is found
try:
    #scrunch the data
    ar = psrchive.Archive.load(filename)
    ar.dedisperse()
    ar.remove_baseline()
    ar.fscrunch()
    ar.tscrunch()
    #Generate x and y data
    prof = ar.get_Profile(0,0,0)
    data = prof.get_amps()

    profile = data.mean(axis=tuple(range(data.ndim - 1)))
    n_bins = len(profile)
    xaxis = np.linspace(0, 1, n_bins, endpoint=False)
    yaxis = profile
    dev = np.std(yaxis)
    A = np.max(yaxis)
    p = xaxis[np.argmax(yaxis)]
    xlength = len(xaxis)
    #splits data down the middle, the respective pulses live on either side of this
    n = len(yaxis)
    split = n // 2

#Returns gaussian noise of off pulse data
    def off_pulse_noise(y=yaxis):
        splityarray = np.array_split(y,5)
        offpulsenoise = np.std(splityarray[2])
        return offpulsenoise


    #function that actually splits data to be analyzed separatly
    def extract_segment(x, y, start, end):
        n = len(y)
        if start < end:
            return x[start:end].copy(), y[start:end].copy()
        else:#Combine wrap around start and end (split in middle so this is archaic)
            x_head = x[start:]
            x_tail = x[:end] + (x[-1] - x[0] + (x[1] - x[0]))
            return (np.concatenate([x_head, x_tail]),
                    np.concatenate([y[start:], y[:end]]))

    segments = [
        extract_segment(xaxis, yaxis, split, (split + n // 2) % n),
        extract_segment(xaxis, yaxis, (split + n // 2) % n, split),
    ]
    # Choose 25 points on either side of critical vlaue
    pointstaken = 25
    

    #Finds interval where fitting point will occut, takes in number of points as input
    def FindCriticalInterval(x, x0, n=pointstaken):
        #make sure this isn't a float value
        half = n // 2
        # Sort the data then take closest points on either end of the critical x value, we do this for half of the points taken value
        idx_sorted = np.argsort(x)
        pos = np.searchsorted(x[idx_sorted], x0)
        left  = idx_sorted[max(0, pos - half):pos]
        right = idx_sorted[pos:pos + half]
        #combine the two arrays of points on either side and sort it
        return np.sort(np.concatenate([left, right]))
        
        
        #Linear polynomial fit
    def Polynomial_fit(xinterval, yinterval, amp):
        poly_fit = lambda x, a, b: a + b*x
        popt, pcov = curve_fit(poly_fit, xinterval, yinterval)
        a, b = popt
        #Look for where the line crosses the half max of the gaussian
        hhy = ((amp/2) - a) / b
        noise = off_pulse_noise(yaxis)/b
        return popt, hhy, noise

    def meanfitting(xinterval, yinterval, amp, pointstaken):
        hhyarr = []
        offpulsearr = []
        n_pts = len(xinterval)
        #Repeat this trial of fitting lines lots of times
        for i in range(1000):
            #do trial with random points
            nums = random.sample(range(n_pts), min(pointstaken//2, n_pts))
            xfilt = np.array([xinterval[j] for j in nums])
            yfilt = np.array([yinterval[j] for j in nums])
            #don't double points
            if np.max(xfilt) - np.min(xfilt) < 1e-10:
                continue
            
            #polynomial fit
            try:
                popt, hhy, off_pulse_noise = Polynomial_fit(xfilt, yfilt, amp)
                hhyarr.append(hhy)
                offpulsearr.append(off_pulse_noise)
            except (RuntimeError, ValueError):
                pass
        #NO POINTS!!!!!!
        if len(hhyarr) == 0:
            raise RuntimeError("meanfitting: no valid fits found")

        #Only take in values within a certain threshold
        hhyarr = np.array(hhyarr)
        q1, q3 = np.percentile(hhyarr, 25), np.percentile(hhyarr, 75)
        iqr = q3 - q1
        mask = (hhyarr >= q1 - 3*iqr) & (hhyarr <= q3 + 3*iqr)
        hhyarr_clean = hhyarr[mask] if mask.any() else hhyarr

        print(np.mean(offpulsearr))
        return np.mean(hhyarr_clean), list(hhyarr_clean), np.mean(offpulsearr)


    #Fitting the Gaussian so the critcal interval can be found
    def FittingGaussian(x, y, dev, A, p):
        
        fit_func = lambda x, a, b, sigma: a*np.exp((-(x-b)**2)/(2*sigma**2))
        p0 = [np.max(y), x[np.argmax(y)], (x[-1]-x[0])/10]
        popt, pcov = curve_fit(fit_func, x, y, p0=p0, maxfev=100000)
        a, b, sigma = popt


        #Centroid of critical interval points
        x1 = b - sigma*np.sqrt(2*np.log(2))
        x2 = b + sigma*np.sqrt(2*np.log(2))

        #Generate lists of critical points that we will truncate
        x1_idx = FindCriticalInterval(x, x1, pointstaken)
        y1interv = y[x1_idx]
        x1interv = x[x1_idx]

        y1Cinterv = []
        x1Cinterv = []


        #Truncate points outside of region of interest
        for i in range(len(y1interv)):
            if 0.35 * a < y1interv[i] < 0.7 * a:
                x1Cinterv.append(x1interv[i])
                y1Cinterv.append(y1interv[i])
        #IF there are NO points run this part
        if len(y1Cinterv) == 0 or len(y1Cinterv) == 1:
            best_pair1 = None
            best_score1 = -np.inf
            #Assign score value to points based on how close they are
            for p1 in range(len(y1interv)):
                for q1 in range(p1 + 1, len(y1interv)):
                    lo1 = min(y1interv[p1], y1interv[q1])
                    hi1 = max(y1interv[p1], y1interv[q1])
                    #find separation between two points so we can decide if they're far enough apart to fit with
                    separation1 = hi1 - lo1
                    lo_violation1 = max(0, 0.35 * a - lo1) + max(0, lo1 - 0.7 * a)
                    hi_violation1 = max(0, 0.35 * a - hi1) + max(0, hi1 - 0.7 * a)
                    total_violation1 = lo_violation1 + hi_violation1
                    score1 = separation1 - total_violation1
                    if score1 > best_score1:
                        best_score1 = score1
                        best_pair1 = (p1, q1)
            if best_pair1 is not None:
                p1, q1 = best_pair1
                x1Cinterv = [x1interv[p1], x1interv[q1]]
                y1Cinterv = [y1interv[p1], y1interv[q1]]


        #This is identical to the part above
        x2_idx = FindCriticalInterval(x, x2, pointstaken)
        y2interv = y[x2_idx]
        x2interv = x[x2_idx]

        y2Cinterv = []
        x2Cinterv = []

        for i in range(len(y2interv)):
            if 0.35 * a < y2interv[i] < 0.7 * a:
                x2Cinterv.append(x2interv[i])
                y2Cinterv.append(y2interv[i])

        if len(y2Cinterv) == 0 or len(y2Cinterv) == 1:
            best_pair2 = None
            best_score2 = -np.inf
            for p2 in range(len(y2interv)):
                for q2 in range(p2 + 1, len(y2interv)):
                    lo2 = min(y2interv[p2], y2interv[q2])
                    hi2 = max(y2interv[p2], y2interv[q2])
                    separation2 = hi2 - lo2
                    lo_violation2 = max(0, 0.35 * a - lo2) + max(0, lo2 - 0.7 * a)
                    hi_violation2 = max(0, 0.35 * a - hi2) + max(0, hi2 - 0.7 * a)
                    total_violation2 = lo_violation2 + hi_violation2
                    score2 = separation2 - total_violation2
                    if score2 > best_score2:
                        best_score2 = score2
                        best_pair2 = (p2, q2)
            if best_pair2 is not None:
                p2, q2 = best_pair2
                x2Cinterv = [x2interv[p2], x2interv[q2]]
                y2Cinterv = [y2interv[p2], y2interv[q2]]
        #half height arrays
        hhy1, hyarr1, offpulsestd1 = meanfitting(x1Cinterv, y1Cinterv, a, pointstaken)
        hhy2, hyarr2, offpulsestd2 = meanfitting(x2Cinterv, y2Cinterv, a, pointstaken)
        sDEV = np.sqrt(offpulsestd1**2 + offpulsestd2**2)
        
        #pulse width obviously difference of pulse side locations
        pulse_width = np.abs(hhy2 - hhy1)
        
        #Get uncertainty
        n_boot = min(len(hyarr1), len(hyarr2))
        PWarray = [np.abs(hyarr2[i] - hyarr1[i]) for i in range(n_boot)]
        dhhy = np.std(PWarray)

        return pulse_width, dev, sigma, a, b, dhhy, sDEV

    #Normalize to give values in terms of bins
    def Normalize(k):
        pulse_width, _, sigma, a, b, dhh, sDEV = FittingGaussian(segments[k][0], segments[k][1], dev, A, p)
        NormalPW = np.abs(xlength * pulse_width)
        Normaldhh = np.sqrt((xlength * dhh)**2+(xlength *sDEV)**2)
        NormalSigma = np.sqrt((xlength * sigma)**2 + (xlength *sDEV)**2)
        return Normaldhh, NormalPW, NormalSigma

    for k in range(len(segments)):
        Normalizedhh, NormalPW, NormalSigma = Normalize(k)
        print("=========================================")
        print("calculated Pulse Width:", NormalPW, "pm", Normalizedhh)
        print("=========================================")
        #SAVE MJD DATE
        MJD1 = filename[17:22]
        MJD2 = filename[23:28]
        with open("convergence.txt", "a") as file:
            file.write(f"{MJD1}.{MJD2} {NormalPW} {Normalizedhh} ")

    with open("convergence.txt", "a") as file:
        file.write(f"\n")

except Exception as e:
    print(f"FAILED: {filename}")
    print(e)
    failcount += 1
    with open("failed_files.txt", "a") as f:
        f.write(filename + "\n")

print("-- Failed on ", failcount, " files --")

