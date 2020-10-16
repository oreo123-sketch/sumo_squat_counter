from obschart import ApplicationRequestHandler, Request
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

#ROS -> Running on spot
#JJ -> Jumping Jacks

def smooth(new_averages, box_size):
    box = np.ones(box_size) / box_size
    y_smooth = np.convolve(new_averages, box, mode="same")
    return y_smooth
def configure_app(sensor_data, p, w, d):
    conf_squats_std = 3                     # Default value of Calibration squats
    count = count_peaks(sensor_data, p, w, d)
    if count==conf_squats_std:
        return [p, w, d]                    #No need to change the parameters
    elif count < conf_squats_std:
        while 1:
            if p>0.3:                       #min value of prominence:0.3
                p-=0.1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if w>3:                         #min value of width:3
                w-=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if d>10:                        #min value of distance:10
                d-=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if p<=0.3 and w<=3 and d<=10:       #Lower Limits
                return [0, 0, 0]                #RECALIBRATE
    elif count > conf_squats_std:
        while 1:
            if p<0.7:                       #max value of prominence: 0.7
                p+=0.1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if w<10:                        #max value of width: 10
                w+=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if d<20:                        #max value of distance: 20
                d+=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_squats_std:
                    return [p, w, d]
            if p>=0.7 and w>=10 and d>=20:      #Upper limits
                return [0, 0, 0]                #RECALIBRATE

def configure_ROS(sensor_data, p, d):
    conf_ROS_std = 10                        # Default value of Calibration squats
    w = 0                                    # Width=0
    count = count_peaks(sensor_data, p, w, d)       
    if count==conf_ROS_std:
        return [p, d]                        #No need to change the parameters
    elif count < conf_ROS_std:
        while 1:
            if p>0.1:                       #min value of prominence:0.1
                p-=0.1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_ROS_std:
                    return [p, d]
            
            if d>2:                        #min value of distance:2
                d-=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_ROS_std:
                    return [p, d]
            if p<=0.1 and d<=2:               #Lower Limits
                return [0, 0]                #RECALIBRATE

    elif count > conf_ROS_std:
        while 1:
            
            if d<7:                        #max value of distance: 7
                d+=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_ROS_std:
                    return [p, d]
            if p<0.3:                       #max value of prominence: 0.3
                p+=0.1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_ROS_std:
                    return [p, d]

            if p>=0.3 and d>=7:                 #Upper limits
                return [0, 0]                   #RECALIBRATE
def configure_JJ(sensor_data, p, d):
    conf_JJ_std = 5                        # Default value of Calibration JJ
    w = 0                                    # Width=0
    count = count_peaks(sensor_data, p, w, d)       
    if count==conf_JJ_std:
        return [p, d]                        #No need to change the parameters
    elif count < conf_JJ_std:
        while 1:
            if p>0.2:                       #min value of prominence:0.2
                p-=0.1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_JJ_std:
                    return [p, d]
            
            if d>3:                        #min value of distance:3
                d-=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_JJ_std:
                    return [p, d]
            if p<=0.2 and d<=3:               #Lower Limits
                return [0, 0]                #RECALIBRATE

    elif count > conf_JJ_std:
        while 1:
            if d<7:                        #max value of distance: 7
                d+=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_JJ_std:
                    return [p, d]
            if p<0.3:                       #max value of prominence: 0.3
                p+=0.1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_JJ_std:
                    return [p, d]

            if p>=0.3 and d>=7:                 #Upper limits
                return [0, 0]                   #RECALIBRATE

def count_peaks(input, prom, wid, dist):
    peaks, _ = find_peaks(input, prominence=prom, distance=dist, width=wid)    #'prominence' to detect 'true' peaks
                                                                                #'distance' to ignore rapid peaks
    try:
        if peaks[0] < 10:
            peaks = np.delete(peaks, 0)
    except:
        peaks = []
    return len(peaks)

def eval_and_smooth(data):
        dictData = eval(data)
        data_numbers = pd.DataFrame(dictData["accelerometer"])
        data_numbers["smoothed_x"] = smooth(data_numbers["x"], 4)
        data_numbers["smoothed_y"] = smooth(data_numbers["y"], 4)
        data_numbers["smoothed_z"] = smooth(data_numbers["z"], 4)
        data_averages = (data_numbers["x"] + data_numbers["y"] + data_numbers["z"]) / 3
        data_smoothed_averages = (
            smooth(data_numbers["x"], 4) + smooth(data_numbers["y"], 4) + smooth(data_numbers["z"], 4)
        ) / 3

        data_mean = data_averages.mean()
        data_smoothed_mean = data_smoothed_averages.mean()
        data_new_averages = data_averages - data_mean
        data_new_smoothed_averages = data_smoothed_averages - data_smoothed_mean

        data_numbers["normalized_averages"] = data_averages
        data_numbers["smoothed_averages"] = data_smoothed_averages
        data_numbers["normalised_averages"] = data_new_averages
        data_numbers["normalised_smoothed_averages"] = data_new_smoothed_averages
        data_numbers["even_more_smoothed_normalised_averages"] = smooth(data_new_smoothed_averages, 6)

        return data_numbers
def ROS_eval(data):
        dictData = eval(data)
        data_numbers = pd.DataFrame(dictData["accelerometer"])
        data_numbers["smoothed_x"] = smooth(data_numbers["x"], 2)
        data_numbers["smoothed_y"] = smooth(data_numbers["y"], 2)
        data_numbers["smoothed_z"] = smooth(data_numbers["z"], 2)
        data_averages = (data_numbers["x"] + data_numbers["y"] + data_numbers["z"]) / 3
        #data_smoothed_averages = (
        #    smooth(data_numbers["x"], 2) + smooth(data_numbers["y"], 2) + smooth(data_numbers["z"], 2)
        # ) / 3

        # data_mean = data_averages.mean()
        # data_smoothed_mean = data_smoothed_averages.mean()
        # data_new_averages = data_averages - data_mean
        # data_new_smoothed_averages = data_smoothed_averages - data_smoothed_mean

        data_numbers["averages"] = data_averages
        data_numbers["normalized_averages"] = (data_averages/data_averages.max())*(-1)  #Flip the peaks 
        
        # data_numbers["smoothed_averages"] = data_smoothed_averages
        # data_numbers["normalised_averages"] = data_new_averages
        # data_numbers["normalised_smoothed_averages"] = data_new_smoothed_averages
        # data_numbers["even_more_smoothed_normalised_averages"] = smooth(data_new_smoothed_averages, 6)

        return data_numbers
class SumoSquatCounter(ApplicationRequestHandler):
    def instructions_step(self):
        return self.client.build_step("Units").add_youtube_video('9ZuXKqRbT9k').add_text('1. Put your phone in your hand\n\n2. Start sensor and do as many sumo squats as you can. \n\n3. Stop the sensor and save to see your results! ')

    def information_step(self):
        return self.client.build_step("Information").add_text('Looks like you are going too fast.\n\n Slow down your pace next time!')

    def configuration_step(self, text='Perform 3 squats in succession to configure your device'):

        return self.client.build_step("Configuration").add_text(text).add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Configuration1",)
            # ).add_sensor_field(
            # "Sensor",
            # required=True,
            # samplingFrequency=100,
            # sensorTypes=["accelerometer"],
            # id="Configuration2",)
            # ).add_sensor_field(
            # "Sensor",
            # required=True,
            # samplingFrequency=100,
            # sensorTypes=["accelerometer"],
            # id="Configuration3",
            # )
    def sensor_step(self):
        
        return self.client.build_step("Units").add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Sensor",
            ).add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Sensor2",
            ).add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Sensor3",
            ).add_number_field(
                "How many sumo squats did you actually do?",
                required=True,
                min=1,
                max=9007199254740991,
                step=1,
                id="Sumo Squat Number",
            ).add_number_field(
                "How many Run-on-spot steps did you actually do?",
                required=True,
                min=1,
                max=9007199254740991,
                step=1,
                id="ROS Number",
            ).add_number_field(
                "How many Jumping Jacks did you actually do?",
                required=True,
                min=1,
                max=9007199254740991,
                step=1,
                id="JJ Number",
            ).add_text_field("Enter your name", required=True, id="Name", suggestions=[])   

    def result_step(self, sumo_squat_count, ROS_count, JJ_count, url):
        return (
            self.client.build_step("Result")
            .add_text(
                "You did {} sumo squats, {} Run-on-spot steps and {} Jumping Jacks".format(
                    sumo_squat_count, ROS_count, JJ_count
                )
            )
            .add_text("![]({})".format(url))
        )
        # if sumo_squat_count>0:
        #     return (
        #         self.client.build_step("Result")
        #         .add_text(
        #             "You did {} sumo squats!! 💪💪💪.  Your best sumo squat was number {}".format(
        #                 sumo_squat_count, top_z
        #             )
        #         )
        #         .add_text("![]({})".format(url))
        #     )
        # else:
        #     return (
                
        #         self.client.build_step("Result")
        #         .add_text(
        #             "You did not do any sumo squats.. 😢😢"
        #         )
        #         .add_text("![]({})".format(url))
        #     )

    async def on_request(self, request: Request):
        
        #Default parameters
        sumo_CONST_prom      = 0.3                   #0.3
        sumo_CONST_width     = 6                     #6
        sumo_CONST_distance  = 14                    #14

        ROS_CONST_prom      = 0.2                   #0.2
        ROS_CONST_width     = 0                     #0
        ROS_CONST_distance  = 4                     #4
        
        JJ_CONST_prom      = 0.2                   #0.2
        JJ_CONST_width     = 0                     #0
        JJ_CONST_distance  = 4                     #4

        sumo_reconfig_flag   = True
        ROS_reconfig_flag    = True
        JJ_reconfig_flag     = True

        sumo_config_text     = 'Perform 3 squats in succession to configure your device'
        ROS_config_text      = 'Do 10 Run-on-spot steps'
        JJ_config_text       = 'Do 5 Jumping Jack steps'

        #response             = await request.prompt(self.instructions_step())

        while sumo_reconfig_flag: #or ROS_reconfig_flag:
            
            response = await request.prompt(self.configuration_step(sumo_config_text))
            sumo_raw_conf_data  = response["Configuration1"]
            #ROS_raw_conf_data   = response["Configuration2"]
            #JJ_raw_conf_data    = response["Configuration3"]

            # Function CALL
            sumo_conf_numbers   = eval_and_smooth(sumo_raw_conf_data)           #Evaluates and Smoothens sensory data
            #ROS_conf_numbers    = ROS_eval(ROS_raw_conf_data)
            #JJ_conf_numbers     = ROS_eval(JJ_raw_conf_data)

            sumo_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\JJ_data.csv')
            #ROS_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\ROS_configure_data.csv')
            #JJ_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\JJ_configure_data.csv')
            
            sumo_conf_data  =   sumo_conf_numbers['even_more_smoothed_normalised_averages']
            #ROS_conf_data   =   ROS_conf_numbers['normalized_averages']        #Dealing with averages to compute ROS steps

            sumo_configured_parameters = configure_app(sumo_conf_data, sumo_CONST_prom, sumo_CONST_width, sumo_CONST_distance)    #Configured-parameters received
            print(sumo_configured_parameters)
            sumo_pr_var = sumo_configured_parameters[0]             #Parameters to pass to count function
            sumo_wd_var = sumo_configured_parameters[1]             #
            sumo_dt_var = sumo_configured_parameters[2]             #

            #ROS_configured_parameters = configure_ROS(ROS_conf_data, ROS_CONST_prom, ROS_CONST_distance)
            #print(ROS_configured_parameters)
            # ROS_pr_var = ROS_configured_parameters[0]
            # ROS_wd_var = 0
            # ROS_dt_var = ROS_configured_parameters[1]
            sumo_reconfig_flag = False                              #Break the configuration loop
            #ROS_reconfig_flag = False

            if sumo_pr_var==0 and sumo_wd_var==0 and sumo_dt_var ==0:
                sumo_reconfig_flag = True        #Sumo counter not configured properly
                sumo_config_text = 'Configuration Error!'
            # if ROS_pr_var==0 and ROS_dt_var==0:
            #     ROS_reconfig_flag = True          #ROS counter not configured properly
        #end of while loop
        
        while ROS_reconfig_flag:
            
            response = await request.prompt(self.configuration_step(ROS_config_text))
            #sumo_raw_conf_data  = response["Configuration1"]
            ROS_raw_conf_data   = response["Configuration1"]
            #JJ_raw_conf_data    = response["Configuration3"]

            # Function CALL
            #sumo_conf_numbers   = eval_and_smooth(sumo_raw_conf_data)           #Evaluates and Smoothens sensory data
            ROS_conf_numbers    = ROS_eval(ROS_raw_conf_data)
            #JJ_conf_numbers     = ROS_eval(JJ_raw_conf_data)

            #sumo_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\sumo_configure_data.csv')
            ROS_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\ROS_configure_data.csv')
            #JJ_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\JJ_configure_data.csv')
            
            #sumo_conf_data  =   sumo_conf_numbers['even_more_smoothed_normalised_averages']
            ROS_conf_data   =   ROS_conf_numbers['normalized_averages']        #Dealing with averages to compute ROS steps

            #sumo_configured_parameters = configure_app(sumo_conf_data, sumo_CONST_prom, sumo_CONST_width, sumo_CONST_distance)    #Configured-parameters received
            #print(sumo_configured_parameters)
            # sumo_pr_var = sumo_configured_parameters[0]             #Parameters to pass to count function
            # sumo_wd_var = sumo_configured_parameters[1]             #
            # sumo_dt_var = sumo_configured_parameters[2]             #

            ROS_configured_parameters = configure_ROS(ROS_conf_data, ROS_CONST_prom, ROS_CONST_distance)
            print(ROS_configured_parameters)
            ROS_pr_var = ROS_configured_parameters[0]
            ROS_wd_var = 0
            ROS_dt_var = ROS_configured_parameters[1]
            #sumo_reconfig_flag = False                              #Break the configuration loop
            ROS_reconfig_flag = False

            # if sumo_pr_var==0 and sumo_wd_var==0 and sumo_dt_var ==0:
            #     sumo_reconfig_flag = True        #Sumo counter not configured properly
            #     sumo_config_text = 'Configuration Error!'
            if ROS_pr_var==0 and ROS_dt_var==0:
                ROS_reconfig_flag = True          #ROS counter not configured properly
                ROS_config_text = 'Configuration Error! Please do 10 Run-on-spot steps again'
        #end while loop

        while JJ_reconfig_flag:
            
            response = await request.prompt(self.configuration_step(JJ_config_text))
            #sumo_raw_conf_data  = response["Configuration1"]
            JJ_raw_conf_data   = response["Configuration1"]
            #JJ_raw_conf_data    = response["Configuration3"]

            # Function CALL
            #sumo_conf_numbers   = eval_and_smooth(sumo_raw_conf_data)           #Evaluates and Smoothens sensory data
            JJ_conf_numbers    = eval_and_smooth(JJ_raw_conf_data)
            #JJ_conf_numbers     = ROS_eval(JJ_raw_conf_data)

            #sumo_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\sumo_configure_data.csv')
            JJ_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\JJ_configure_data.csv')
            #JJ_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\JJ_configure_data.csv')
            
            #sumo_conf_data  =   sumo_conf_numbers['even_more_smoothed_normalised_averages']
            JJ_conf_data   =   JJ_conf_numbers['even_more_smoothed_normalised_averages']        #Dealing with averages to compute ROS steps

            #sumo_configured_parameters = configure_app(sumo_conf_data, sumo_CONST_prom, sumo_CONST_width, sumo_CONST_distance)    #Configured-parameters received
            #print(sumo_configured_parameters)
            # sumo_pr_var = sumo_configured_parameters[0]             #Parameters to pass to count function
            # sumo_wd_var = sumo_configured_parameters[1]             #
            # sumo_dt_var = sumo_configured_parameters[2]             #

            JJ_configured_parameters = configure_JJ(JJ_conf_data, JJ_CONST_prom, JJ_CONST_distance)
            print(JJ_configured_parameters)
            JJ_pr_var = JJ_configured_parameters[0]
            JJ_wd_var = 0
            JJ_dt_var = JJ_configured_parameters[1]
            #sumo_reconfig_flag = False                              #Break the configuration loop
            JJ_reconfig_flag = False

            # if sumo_pr_var==0 and sumo_wd_var==0 and sumo_dt_var ==0:
            #     sumo_reconfig_flag = True        #Sumo counter not configured properly
            #     sumo_config_text = 'Configuration Error!'
            if JJ_pr_var==0 and JJ_dt_var==0:
                JJ_reconfig_flag = True          #ROS counter not configured properly
                JJ_config_text = 'Configuration Error! Please do 5 Jumping Jacks again'
        #end while loop
        
        #Sensor data

        response = await request.prompt(self.sensor_step())
        sensor = response["Sensor"]
        number = response["Sumo Squat Number"]
        name = response["Name"]

        ROS_sensor = response["Sensor2"]
        number = response["ROS Number"]

        JJ_sensor = response["Sensor3"]
        number = response["JJ Number"]
        # Function Call
        numbers = eval_and_smooth(sensor)               #Evaluates and smoothens sensory data
        ROS_numbers = ROS_eval(ROS_sensor)
        JJ_numbers = eval_and_smooth(JJ_sensor)

        sumo_squat_count = 0
        top_sumo_squat = 0
        ROS_count = 0
        JJ_count = 0
        
        print('printing data')

        numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\{}.csv'.format('sumo-'+name+number))
        ROS_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\{}.csv'.format('ROS-'+name+number))
        JJ_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\{}.csv'.format('JJ-'+name+number))
        #new_smoothed_averages  = numbers["normalised_smoothed_averages"] #Used in plotting final graph
        

        sumo_count_peaks_data   = numbers['even_more_smoothed_normalised_averages']           #Counting squats
        sumo_squat_count        = count_peaks(sumo_count_peaks_data, sumo_pr_var, sumo_wd_var, sumo_dt_var)
        ROS_count_peaks_data    = ROS_numbers['normalized_averages']
        ROS_count               = count_peaks(ROS_count_peaks_data, ROS_pr_var, ROS_wd_var, ROS_dt_var)
        JJ_count_peaks_data    = JJ_numbers['even_more_smoothed_normalised_averages']
        JJ_count               = count_peaks(JJ_count_peaks_data, JJ_pr_var, JJ_wd_var, JJ_dt_var)
        #sumo_squat_count = count_peaks(x, 0.3, 4, 10)

       

        figure, ax = plt.subplots(1, 1, facecolor="w", edgecolor="k")
        #ax.plot(smooth(new_smoothed_averages, 6), "g-", lw=2)   
        ax.plot(smooth(ROS_count_peaks_data, 2), "g-", lw=2)

        image = await self.client.create_image(figure)
        plt.close(figure)

        #Set output
        await request.set_output(
            self.client.build_feedback_data()
            .add_text_field("Sumo Squat number")
            .add_image_field("Movement graph"),
            [
                "Client did {} sumo squats!! 💪💪💪, {} Run-on-spot Steps, {} Jumping Jacks".format(
                    sumo_squat_count, ROS_count, JJ_count
                ),
                image.url,
            ],
        )

        # if sumo_squat_count>0:
        #     # Set output
        #     await request.set_output(
        #         self.client.build_feedback_data()
        #         .add_text_field("Sumo Squat number")
        #         .add_image_field("Movement graph"),
        #         [
        #             "Client did {} sumo squats!! 💪💪💪.  Best sumo squat was number {}".format(
        #                 sumo_squat_count, top_sumo_squat
        #             ),
        #             image.url,
        #         ],
        #     )
        # else:
        # # Set output
        #     await request.set_output(
        #         self.client.build_feedback_data()
        #         .add_text_field("Sumo squat number")
        #         .add_image_field("Movement graph"),
        #         [
        #             "Client did no sumo squats 😢😢"
        #             ,
        #             image.url,
        #         ],
        #     )
        # End by showing user the results
        #await request.end(self.result_step(sumo_squat_count, top_sumo_squat, image.url))
        await request.end(self.result_step(sumo_squat_count, ROS_count, JJ_count, image.url))
