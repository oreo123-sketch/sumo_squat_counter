from obschart import ApplicationRequestHandler, Request
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import find_peaks



def smooth(new_averages, box_size):
    box = np.ones(box_size) / box_size
    y_smooth = np.convolve(new_averages, box, mode="same")
    return y_smooth


class SumoSquatCounter(ApplicationRequestHandler):
    def instructions_step(self):
        return self.client.build_step("Units").add_youtube_video('9ZuXKqRbT9k').add_text('1. Put your phone in your hand\n\n2. Start sensor and do as many sumo squats as you can. \n\n3. Stop the sensor and save to see your results! ')

    def sensor_step(self):
        return self.client.build_step("Units").add_sensor_field(
            "Sensor",
            required=True,
            samplingFrequency=100,
            sensorTypes=["accelerometer"],
            id="Sensor",
        )

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
        
        response = await request.prompt(self.instructions_step())
        response = await request.prompt(self.sensor_step())
        sensor = response["Sensor"]
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
        # numbers.to_csv('data.csv')
        numbers.to_csv(r'C:\Users\Shayan Haider\Desktop\data.csv')

        x = numbers['even_more_smoothed_normalised_averages']
        peaks, _ = find_peaks(x, prominence=0.5, distance=20, height=[0, 3])    #'prominence' to detect 'true' peaks
                                                                                #'distance' to ignore rapid peaks
                                                                                # 'height' to ignore false 'over-valued' peaks

        try:
            if peaks[0] < 15:
                peaks = np.delete(peaks, 0)
        except:
            peaks = []
        sumo_squat_count = len(peaks)

        #for n in smooth(new_smoothed_averages, 6):
           # no = float(n)
            #if no < bottom_x:
               # bottom_x = no
                #top_sumo_squat = sumo_squat_count + 1
            #if no < -1.3 and up_phase == False:
               # up_phase = True
            #elif no > 0.5:
               # if up_phase == True:
                   # sumo_squat_count += 1
                #up_phase = False

        figure, ax = plt.subplots(1, 1, facecolor="w", edgecolor="k")
        ax.plot(smooth(new_smoothed_averages, 6), "g-", lw=2)   
        # plt.plot(numbers['x'],'o')
        # plt.plot(smooth(new_smoothed_averages, 6), "g-", lw=2)
        # figure = plt.gcf()
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
