from obschart import ApplicationRequestHandler, Request
from obschart.gql import gql
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from time import *
import pickle

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
            if d<9:                        #max value of distance: 9
                d+=1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_JJ_std:
                    return [p, d]
            if p<0.3:                       #max value of prominence: 0.3
                p+=0.1
                count = count_peaks(sensor_data, p, w, d)
                if count==conf_JJ_std:
                    return [p, d]

            if p>=0.3 and d>=9:                 #Upper limits
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
        data_numbers["averages"] = data_averages
        data_numbers["normalized_averages"] = (data_averages/data_averages.max())*(-1)  #Flip the peaks 
        return data_numbers

class SumoSquatCounter(ApplicationRequestHandler):
    def instructions_step(self):
        return self.client.build_step("Units").add_youtube_video('9ZuXKqRbT9k').add_text('1. Put your phone in your hand\n\n2. Start sensor and do as many sumo squats as you can. \n\n3. Stop the sensor and save to see your results! ')
    def information_step(self):
        return self.client.build_step("Information").add_text('Looks like you are going too fast.\n\n Slow down your pace next time!')
    def configuration_step(self, text='Perform 3 squats in succession to configure your device', gifString="\n\n![](https://media.giphy.com/media/RlN58dnfELJUCZEPkr/giphy.gif)\n\n"):

        return self.client.build_step("Configuration").add_text(text).add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Configuration1",
            ).add_text(gifString)
    def sumo_sensor_step(self, time=30, loop_number=1):
        
        return self.client.build_step("Sumo Squats (Round {})".format(loop_number)).add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Sensor",
            ).add_timer_countdown("Tick Tock!", True, "PT{}S".format(time))            
    def ROS_sensor_step(self, time=30, loop_number=1):
        return self.client.build_step("Run-on-spot (Round {})".format(loop_number)).add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Sensor2",
            ).add_timer_countdown("You can do it!", True, "PT{}S".format(time))
    def JJ_sensor_step(self, time=30, loop_number=1):
        return self.client.build_step("Jumping Jacks (Round {})".format(loop_number)).add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Sensor3",
            ).add_timer_countdown("Sweat, Smile and Repeat!", True, "PT{}S".format(time))
    def user_input_timer(self):
        return self.client.build_step("Customize the time intervals!").add_number_field(
                "How many loops you wanna do?",
                required=True,
                min=1,
                max=9007199254740991,
                step=1,
                id="loopNumber",
            ).add_number_field(
                "Time for Sumo Squats? (seconds)",
                required=True,
                min=1,
                max=9007199254740991,
                step=1,
                id="sumoTime",
            ).add_number_field(
                "Time for Run-On-Spot?",
                required=True,
                min=1,
                max=9007199254740991,
                step=1,
                id="rosTime",
            ).add_number_field(
                "Time for Jumping Jacks?",
                required=True,
                min=1,
                max=9007199254740991,
                step=1,
                id="jjTime",
            )
            # .add_text_field("Enter your name", required=True, id="Name", suggestions=[])
    def result_step(self, sumo_squat_count, ROS_count, JJ_count, url, gifs):
        if (0 <= sumo_squat_count < 3) and (0 <= ROS_count < 5) and (0 <= JJ_count < 3):
            return (
                    self.client.build_step("Result")
                    .add_text(
                        "You did {} sumo squats, {} Run-on-spot steps and {} Jumping Jacks".format(
                            sumo_squat_count, ROS_count, JJ_count
                        )
                    )
                    .add_text(gifs[0])
                    .add_text("![]({})".format(url))
                    
            )
        else:
            return (
                    self.client.build_step("Result")
                    .add_text(
                        "You did {} sumo squats, {} Run-on-spot steps and {} Jumping Jacks".format(
                            sumo_squat_count, ROS_count, JJ_count
                        )
                    )
                    .add_text(gifs[1])
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

        responses = await self.client._execute(
        gql(
            """
            query ProgramTrackActionQuery($id: ID!) 
                {
                    programTrackAction(id: $id) 
                        {
                        responses(first:100)
                            {
                                edges
                                {
                                    node
                                    {
                                        #parameters_list
                                        response    
                                        # createdAt
                                        # event{
                                        #     startDate
                                        # }
                                    }
                                }
                            }
                        }
                }
            
        """
        ),
        #{"id": request.action.id},
        {"id": request.action.id},
        )
        #responses.to_csv(r'C:\Users\Shayan Haider\Desktop\response.csv')
        # with open('obj/'+ 'response' + '.pkl', 'wb') as f:
        #     pickle.dump(responses, f, 0)
        
        print(responses)
        
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

        sumo_reconfig_flag   = True                 #True
        ROS_reconfig_flag    = True                 #True
        JJ_reconfig_flag     = True                 #True

        sumo_config_text     = 'Perform 3 squats in succession to configure your device'
        ROS_config_text      = 'Do 10 Run-on-spot steps'
        JJ_config_text       = 'Do 5 Jumping Jack steps'

        sumo_configured_parameters  = [0, 0, 0]
        ROS_configured_parameters = [0, 0, 0]
        JJ_configured_parameters = [0, 0, 0]

        #Gifs
        sumo_gif = "\n\n![](https://media.giphy.com/media/RlN58dnfELJUCZEPkr/giphy.gif)\n\n"
        ROS_gif = "\n\n![](https://media.giphy.com/media/62aGqZoUJYtPsl0Hb0/giphy.gif)\n\n"
        JJ_gif = "\n\n![](https://media.giphy.com/media/4Hx33hvGMdeyK016mT/giphy.gif)\n\n"


        while sumo_reconfig_flag:               #or ROS_reconfig_flag:
            
            response = await request.prompt(self.configuration_step(sumo_config_text, sumo_gif))
            sumo_raw_conf_data  = response["Configuration1"]
        
            # Function CALL
            sumo_conf_numbers   = eval_and_smooth(sumo_raw_conf_data)           #Evaluates and Smoothens sensory data
            sumo_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\JJ_data.csv')
            sumo_conf_data  =   sumo_conf_numbers['even_more_smoothed_normalised_averages']
            sumo_configured_parameters = configure_app(sumo_conf_data, sumo_CONST_prom, sumo_CONST_width, sumo_CONST_distance)    #Configured-parameters received
            print(sumo_configured_parameters)
            sumo_pr_var = sumo_configured_parameters[0]             #Parameters to pass to count function
            sumo_wd_var = sumo_configured_parameters[1]             #
            sumo_dt_var = sumo_configured_parameters[2]             #

            sumo_reconfig_flag = False                              #Break the configuration loop
        
            if sumo_pr_var==0 and sumo_wd_var==0 and sumo_dt_var ==0:
                sumo_reconfig_flag = True                            #Sumo counter not configured properly
                sumo_config_text = 'Configuration Error! Do 3 sumo-squats again'
        #end of while loop
        
        while ROS_reconfig_flag:
            
            response = await request.prompt(self.configuration_step(ROS_config_text, ROS_gif))
            ROS_raw_conf_data   = response["Configuration1"]
            ROS_conf_numbers    = ROS_eval(ROS_raw_conf_data)
            ROS_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\ROS_configure_data.csv')
            ROS_conf_data   =   ROS_conf_numbers['normalized_averages']        #Dealing with averages to compute ROS steps
            ROS_configured_parameters = configure_ROS(ROS_conf_data, ROS_CONST_prom, ROS_CONST_distance)
            print(ROS_configured_parameters)
            ROS_pr_var = ROS_configured_parameters[0]
            ROS_wd_var = 0
            ROS_dt_var = ROS_configured_parameters[1]
            ROS_reconfig_flag = False

            if ROS_pr_var==0 and ROS_dt_var==0:
                ROS_reconfig_flag = True          #ROS counter not configured properly
                ROS_config_text = 'Configuration Error! Please do 10 Run-on-spot steps again'
        #end while loop

        while JJ_reconfig_flag:
            
            response = await request.prompt(self.configuration_step(JJ_config_text, JJ_gif))
            JJ_raw_conf_data   = response["Configuration1"]
            
            # Function CALL
            JJ_conf_numbers    = eval_and_smooth(JJ_raw_conf_data)
            JJ_conf_numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\JJ_configure_data.csv')
            JJ_conf_data   =   JJ_conf_numbers['even_more_smoothed_normalised_averages']        #Dealing with averages to compute ROS steps
            JJ_configured_parameters = configure_JJ(JJ_conf_data, JJ_CONST_prom, JJ_CONST_distance)
            print(JJ_configured_parameters)
            JJ_pr_var = JJ_configured_parameters[0]
            JJ_wd_var = 0                                               #Parameters to pass to count function
            JJ_dt_var = JJ_configured_parameters[1]

            JJ_reconfig_flag = False            #Configuration successful!

            if JJ_pr_var==0 and JJ_dt_var==0:
                JJ_reconfig_flag = True          #ROS counter not configured properly
                JJ_config_text = 'Configuration Error! Please do 5 Jumping Jacks again'
        #end while loop
        
        #parameters list
        parameters_list = []
        parameters_list.append(sumo_configured_parameters)
        parameters_list.append(ROS_configured_parameters)
        parameters_list.append(JJ_configured_parameters)

        #count variables
        sumo_squat_count = 0
        top_sumo_squat = 0
        ROS_count = 0
        JJ_count = 0

        #Timer
        sumo_time   = 20                    #Seconds
        ROS_time    = 20
        JJ_time     = 20

        #Workout loops
        workoutLoops = 1

        #Time interval inputs from user
        user_time_input     = await request.prompt(self.user_input_timer())
        workoutLoops        = int(user_time_input["loopNumber"])
        sumo_time           = int(user_time_input["sumoTime"])
        ROS_time            = int(user_time_input["rosTime"])
        JJ_time             = int(user_time_input["jjTime"])

        #Appreciation gifs
        gifs = [
            
            "\n\n![](https://media.giphy.com/media/kaa2PfVyAZ1ak7Z119/giphy.gif)\n\n",                                      #Dancing lady (Funny gif)
            "\n\n![](https://media.giphy.com/media/KEVNWkmWm6dm8/giphy.gif)\n\n",       #Victory

        ]
        #HIIT Loop
        for x in range(workoutLoops):
            currentLoop = x+1
            response = await request.prompt(self.sumo_sensor_step(sumo_time, currentLoop))
            sensor = response["Sensor"]
            numbers = eval_and_smooth(sensor)               #Evaluates and smoothens sensory data
            sumo_count_peaks_data   = numbers['even_more_smoothed_normalised_averages']           #Counting squats
            sumo_squat_count        += count_peaks(sumo_count_peaks_data, sumo_pr_var, sumo_wd_var, sumo_dt_var)
            #number = response["Sumo Squat Number"]
            #name = response["Name"]

            response = await request.prompt(self.ROS_sensor_step(ROS_time, currentLoop))
            ROS_sensor = response["Sensor2"]
            ROS_numbers = ROS_eval(ROS_sensor)
            ROS_count_peaks_data    = ROS_numbers['normalized_averages']
            ROS_count               += count_peaks(ROS_count_peaks_data, ROS_pr_var, ROS_wd_var, ROS_dt_var)

            response = await request.prompt(self.JJ_sensor_step(JJ_time, currentLoop))
            JJ_sensor = response["Sensor3"]
            JJ_numbers = eval_and_smooth(JJ_sensor)
            JJ_count_peaks_data    = JJ_numbers['even_more_smoothed_normalised_averages']
            JJ_count               += count_peaks(JJ_count_peaks_data, JJ_pr_var, JJ_wd_var, JJ_dt_var)

            print('printing data')
        #End loop

        figure, ax = plt.subplots(1, 1, facecolor="w", edgecolor="k")
        ax.plot(smooth(sumo_count_peaks_data, 6), "g-", lw=2)   
        #ax.plot(smooth(ROS_count_peaks_data, 2), "g-", lw=2)

        image = await self.client.create_image(figure)
        plt.close(figure)

        #Set output - make sure that the output has the same structure each time
        if (0 <= sumo_squat_count < 3) and (0 <= ROS_count < 5) and (0 <= JJ_count < 3):
            await request.set_output(
                self.client.build_feedback_data()
                .add_text_field("Sumo Squat number")
                .add_text(gifs[0])
                .add_text_field("{}".format(parameters_list))
                .add_image_field("Movement graph"),
                [
                    "Client did {} sumo squats, {} Run-on-spot Steps, {} Jumping Jacks".format(
                        sumo_squat_count, ROS_count, JJ_count
                    ),
                    image.url,
                ],
                 
            )#.add_text("{}".format(parameters_list))
        else:
            await request.set_output(
                self.client.build_feedback_data()
                .add_text_field("Sumo Squat number")
                .add_text(gifs[1])
                .add_text_field("{}".format(parameters_list))
                .add_image_field("Movement graph"),
                [
                    "Client did {} sumo squats!! 💪💪💪, {} Run-on-spot Steps, {} Jumping Jacks".format(
                        sumo_squat_count, ROS_count, JJ_count
                    ),
                    image.url,
                ],
            )#.add_text("{}".format(parameters_list))

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
        await request.end(self.result_step(sumo_squat_count, ROS_count, JJ_count, image.url, gifs))
