
import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstApp", "1.0")


import keyboard
import uuid
from time import sleep, time
from gi.repository import Gst, GstApp, GLib
from threading import Thread

array = []


def on_buffer(sink, data):
    global array
    sample = sink.emit("pull-sample")
    if isinstance(sample, Gst.Sample):
        buffer = sample.get_buffer()
        # caps_format = sample.get_caps().get_structure(0)
        # w, h = caps_format.get_value('width'), caps_format.get_value('height')
        array = buffer.extract_dup(0, buffer.get_size())
        return Gst.FlowReturn.OK
    return Gst.FlowReturn.ERROR


if __name__ == '__main__':

    _ = GstApp

    Gst.init()

    main_loop = GLib.MainLoop()
    thread = Thread(target=main_loop.run)
    thread.start()

    pipeline = Gst.parse_launch(
        'nvarguscamerasrc sensor_id=0 tnr-strength=1 tnr-mode=2 ee-strength=0 ! video/x-raw(memory:NVMM),width=1280, height=720, framerate=120/1, format=NV12 ! tee name=t ! queue ! videoconvert ! autovideosink t. ! queue ! nvvidconv flip-method=0 ! jpegenc ! appsink emit-signals=True sync=false drop=true ')
    pipeline.set_state(Gst.State.PLAYING)
    appsink = pipeline.get_by_name("appsink0")
    appsink.connect("new-sample", on_buffer, None)

    while True:
        sleep(0.1)
        if keyboard.is_pressed('p'):
            start_time = time()
            # sample = appsink.emit("pull-sample")
            # array = to_bytes(sample)
            # print(array)
            print('oh snap')
            #     sample = appsink.pull_sample()
            #     data = to_bytes(sample)
            filename = f"/home/nano/Pictures/{uuid.uuid4()}.jpg"
            f = open(filename, 'wb')
            f.write(array)
            f.close
            end_time = time()
            print(f"time taken: {end_time - start_time}")
        if keyboard.is_pressed('q'):
            print(" from qute")
            break

    pipeline.set_state(Gst.State.NULL)
    main_loop.quit()
