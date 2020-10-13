from obschart import ApplicationRequestHandler, Request
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import find_peaks



def smooth(new_averages, box_size):
    box = np.ones(box_size) / box_size
    y_smooth = np.convolve(new_averages, box, mode="same")
    return y_smooth
def configure_app(sensor_data, p, w, d):
    conf_squats_std = 3
    count = count_peaks(sensor_data, p, w, d)
    if count==conf_squats_std:
        return [p, w, d]
    elif count < conf_squats_std:
        while 1:
            if p>0.3:
                p-=0.1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if w>3:
                w-=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if d>10:
                d-=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if p<=0.3 and w<=3 and d<=10:       #Lower Limits
                return "Error: Recalibrate"     #Modify this line for Recalibration process
    elif count > conf_squats_std:
        while 1:
            if p<0.7:
                p+=0.1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if w<10:
                w+=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if d<20:
                d+=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if p>=0.7 and w>=10 and d>=20:      #Upper limits
                return "Error: Recalibrate"     #Modify this line for Recalibration process

def count_peaks(input, prom, wid, dist):
    peaks, _ = find_peaks(input, prominence=prom, distance=dist, width=wid)    #'prominence' to detect 'true' peaks
                                                                                #'distance' to ignore rapid peaks
    try:
        if peaks[0] < 10:
            peaks = np.delete(peaks, 0)
    except:
        peaks = []
    return len(peaks)


class SumoSquatCounter(ApplicationRequestHandler):
    def instructions_step(self):
        return self.client.build_step("Units").add_youtube_video('9ZuXKqRbT9k').add_text('1. Put your phone in your hand\n\n2. Start sensor and do as many sumo squats as you can. \n\n3. Stop the sensor and save to see your results! ')

    def information_step(self):
        return self.client.build_step("Information").add_text('Looks like you are going too fast.\n\n Slow down your pace next time!')

    def configuration_step(self):
        return self.client.build_step("Configuration").add_text('Perform 3 squats in succession to configure your device').add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Configuration",
            )
    def sensor_step(self):
        
        return self.client.build_step("Units").add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Sensor",
            ).add_number_field(
                "How many sumo squats did you actually do?",
                required=True,
                min=1,
                max=9007199254740991,
                step=1,
                id="Sumo Squat Number",
            ).add_text_field("Enter your name", required=True, id="Name", suggestions=[])   

    def result_step(self, sumo_squat_count, top_z, url):
        if sumo_squat_count>0:
            return (
                self.client.build_step("Result")
                .add_text(
                    "You did {} sumo squats!! 💪💪💪.  Your best sumo squat was number {}".format(
                        sumo_squat_count, top_z
                    )
                )
                .add_text("![]({})".format(url))
            )
        else:
            return (
                
                self.client.build_step("Result")
                .add_text(
                    "You did not do any sumo squats.. 😢😢"
                )
                .add_text("![]({})".format(url))
            )

    async def on_request(self, request: Request):
        
        #Default parameters
        pr_var = 0.3                    #0.3
        wd_var = 6                      #6
        dt_var = 14                     #14

        response = await request.prompt(self.instructions_step())
        response = await request.prompt(self.configuration_step())
        conf_data = response["Configuration"]
        dictConf = eval(conf_data)
        conf_numbers = pd.DataFrame(dictConf["accelerometer"])
        conf_numbers["smoothed_x"] = smooth(conf_numbers["x"], 4)
        conf_numbers["smoothed_y"] = smooth(conf_numbers["y"], 4)
        conf_numbers["smoothed_z"] = smooth(conf_numbers["z"], 4)
        conf_averages = (conf_numbers["x"] + conf_numbers["y"] + conf_numbers["z"]) / 3
        conf_smoothed_averages = (
            smooth(conf_numbers["x"], 4) + smooth(conf_numbers["y"], 4) + smooth(conf_numbers["z"], 4)
        ) / 3

        conf_mean = conf_averages.mean()
        conf_smoothed_mean = conf_smoothed_averages.mean()
        conf_new_averages = conf_averages - conf_mean
        conf_new_smoothed_averages = conf_smoothed_averages - conf_smoothed_mean

        conf_numbers["averages"] = conf_averages
        conf_numbers["smoothed_averages"] = conf_smoothed_averages
        conf_numbers["normalised_averages"] = conf_new_averages
        conf_numbers["normalised_smoothed_averages"] = conf_new_smoothed_averages
        conf_numbers["even_more_smoothed_normalised_averages"] = smooth(conf_new_smoothed_averages, 6)
        conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\conf.csv')
        data_to_be_conf = conf_numbers['even_more_smoothed_normalised_averages']
        configured_parameters = configure_app(data_to_be_conf, pr_var, wd_var, dt_var)
        print(configured_parameters)
        pr_var = configured_parameters[0]
        wd_var = configured_parameters[1]
        dt_var = configured_parameters[2]   #Updating new parameters
        #Sensor data

        response = await request.prompt(self.sensor_step())
        sensor = response["Sensor"]
        number = response["Sumo Squat Number"]
        name = response["Name"]

        dictNumbers = eval(sensor)
        numbers = pd.DataFrame(dictNumbers["accelerometer"])
        #print(numbers)
        
        sumo_squat_count = 0
        #bottom_x = 0
        top_sumo_squat = 0
        #up_phase = False

        numbers["smoothed_x"] = smooth(numbers["x"], 4)
        numbers["smoothed_y"] = smooth(numbers["y"], 4)
        numbers["smoothed_z"] = smooth(numbers["z"], 4)
        averages = (numbers["x"] + numbers["y"] + numbers["z"]) / 3
        smoothed_averages = (
            smooth(numbers["x"], 4) + smooth(numbers["y"], 4) + smooth(numbers["z"], 4)
        ) / 3

        mean = averages.mean()
        smoothed_mean = smoothed_averages.mean()
        new_averages = averages - mean
        new_smoothed_averages = smoothed_averages - smoothed_mean

        numbers["averages"] = averages
        numbers["smoothed_averages"] = smoothed_averages
        numbers["normalised_averages"] = new_averages
        numbers["normalised_smoothed_averages"] = new_smoothed_averages
        numbers["even_more_smoothed_normalised_averages"] = smooth(new_smoothed_averages, 6)
        print('printing data')
        numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\{}.csv'.format(name+number))
        

        

        #Using smoothened data and passing it to counter function
        x = numbers['even_more_smoothed_normalised_averages']
        sumo_squat_count = count_peaks(x, pr_var, wd_var, dt_var)
        #sumo_squat_count = count_peaks(x, 0.3, 4, 10)

       

        figure, ax = plt.subplots(1, 1, facecolor="w", edgecolor="k")
        ax.plot(smooth(new_smoothed_averages, 6), "g-", lw=2)   
       
        image = await self.client.create_image(figure)
        plt.close(figure)
        if sumo_squat_count>0:
            # Set output
            await request.set_output(
                self.client.build_feedback_data()
                .add_text_field("Sumo Squat number")
                .add_image_field("Movement graph"),
                [
                    "Client did {} sumo squats!! 💪💪💪.  Best sumo squat was number {}".format(
                        sumo_squat_count, top_sumo_squat
                    ),
                    image.url,
                ],
            )
        else:
        # Set output
            await request.set_output(
                self.client.build_feedback_data()
                .add_text_field("Sumo squat number")
                .add_image_field("Movement graph"),
                [
                    "Client did no sumo squats 😢😢"
                    ,
                    image.url,
                ],
            )
        # End by showing user the results
        await request.end(self.result_step(sumo_squat_count, top_sumo_squat, image.url))
