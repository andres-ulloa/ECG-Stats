import numpy as np
import QRS_Detector as QRS
import json 

import sys

arg_ecg_data = sys.argv[1]
arg_samples_per_sec = int(sys.argv[2])
arg_num_samples = int(sys.argv[3])


class ECGFeaturesExtractor:

    

    def __init__(self, samples_per_sec, json_ecg_data, num_samples):


        self.samples_per_sec = samples_per_sec
        self.json_ecg_data = json_ecg_data
        self.RR_interval_list = list()
        self.num_heart_beats = 0
        self.R_magnitude_vector = list()
        self.num_samples = num_samples
        self.FULL_MIN = 60000

        if samples_per_sec != 0: 
            self.sampling_frecuency = 1/samples_per_sec 
        else:
            print('Invalid sampling period = ', samples_per_sec)
            exit(0)
        

    def extract_R_peak_features(self, detected_qrs):
        IS_QRS_PEAK = 1
        RR_interval_counter = 0
        in_between_peaks = False
        for sample_index in range(0, len(detected_qrs)):
            label = detected_qrs[sample_index,1]
            if int(label) == IS_QRS_PEAK:
                self.R_magnitude_vector.append(detected_qrs[sample_index,0])
                self.num_heart_beats += 1
                if in_between_peaks == False:
                    in_between_peaks = True
                else:
                    self.RR_interval_list.append(RR_interval_counter * self.sampling_frecuency)
                    RR_interval_counter = 0
            if in_between_peaks == True:
                RR_interval_counter += 1
        self.RR_interval_list.append(RR_interval_counter * self.sampling_frecuency)


    def generate_features_vector(self):
        detector = QRS.QRSDetectorOffline(self.json_ecg_data)
        detected_qrs = detector.get_detected_ecg_peaks()
        self.extract_R_peak_features(detected_qrs)
        mean_RR_interval = self.compute_mean(self.RR_interval_list)
        print("RR intervals = ", self.RR_interval_list)
        print("R mags = ", self.R_magnitude_vector)
        beats_per_min = self.FULL_MIN/mean_RR_interval
        features = {}
        features["max_mag"] = self.get_max_ECG_magnitude()
        features["mean_peak_magnitude"] = self.compute_mean(self.R_magnitude_vector)
        features["mean_RR_interval"] = self.compute_mean(self.RR_interval_list)
        features["beats_per_min"]  = beats_per_min
        return self.dic_to_json(features)


    def dic_to_json(self, dic):
        return json.dumps(dic, ensure_ascii = False)

    def get_max_ECG_magnitude(self):
        return max(self.R_magnitude_vector)

    def compute_mean(self, list):
        return sum(list)/len(list)

""" ---------------------------------------------------------------------------------------------------------------------------------"""    
""" ---------------------------------------------------------------------------------------------------------------------------------"""  
""" ---------------------------------------------------------------------------------------------------------------------------------"""  
""" ---------------------------------------------------------------------------------------------------------------------------------"""  

#MAIN INTERFACE METHOD 

def run_feature_extraction(json_ecg_data, samples_per_sec, num_samples):
    extractor = ECGFeaturesExtractor(samples_per_sec, json_ecg_data, num_samples)
    return extractor.generate_features_vector()

"""
THE METHODS BELLOW ARE FOR TESTING ONLY

"""
def to_json(np_array):
    dict = {}
    dict["signal"] = np_array.tolist()
    return json.dumps(dict, ensure_ascii=False) 


def load_one_column_file(path):
    ecg_data = np.loadtxt(path, delimiter="\n")
    return ecg_data

def load_two_column_file(path):
    ecg_data = np.loadtxt(path, skiprows = 1, delimiter = ",")[:,1]
    return ecg_data



if __name__ == "__main__":
    arg_ecg_data = json.loads(arg_ecg_data)
    sys.stdout.write(run_feature_extraction(arg_ecg_data, arg_samples_per_sec, arg_num_samples))
    sys.exit(0)
    """ecg_data = load_two_column_file("ecg_data_2.csv")
    json_ecg_data = to_json(ecg_data)
    print(run_feature_extraction(json_ecg_data, 250, 935))
    """