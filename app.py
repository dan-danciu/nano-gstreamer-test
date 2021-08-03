
import gi
gi.require_version("Gst", "1.0")
gi.require_version("GLib", "2.0")
gi.require_version("GObject", "2.0")


import keyboard
import uuid
import logging
from time import sleep, time
from gi.repository import Gst, GObject, GLib
from threading import Thread

array = []
logging.basicConfig(level=logging.DEBUG,
                    format="[%(name)s] [%(levelname)8s] - %(message)s")
logger = logging.getLogger(__name__)


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

    _ = GObject

    Gst.init()

    main_loop = GLib.MainLoop()
    thread = Thread(target=main_loop.run)
    thread.start()

    source = Gst.ElementFactory.make("nvarguscamerasrc", "source")
    source.props.sensor_id = 0
    source.set_property("tnr-strength", 1)
    source.set_property("tnr-mode", 2)
    caps = Gst.Caps.from_string(
        "video/x-raw(memory:NVMM),width=1280, height=720, framerate=120/1, format=NV12")
    filter = Gst.ElementFactory.make("capsfilter", "filter")
    filter.set_property("caps", caps)
    tee = Gst.ElementFactory.make("tee", "tee")

    queue_jpeg = Gst.ElementFactory.make("queue", "jpegq")
    nvvidconv = Gst.ElementFactory.make("nvvidconv", None)
    nvvidconv.set_property("flip-method", 0)

    jpeg_enc = Gst.ElementFactory.make("jpegenc", None)
    appsink = Gst.ElementFactory.make("appsink", None)
    appsink.set_property("emit-signals", True)
    appsink.set_property("sync", False)
    appsink.set_property("drop", True)

    queue_stream = Gst.ElementFactory.make("queue", "streamq")
    videoconvert_stream = Gst.ElementFactory.make("videoconvert", None)
    autovideosink = Gst.ElementFactory.make("autovideosink", None)

    pipeline = Gst.Pipeline.new("test-pipeline")
    pipeline.add(source)
    pipeline.add(filter)
    pipeline.add(tee)
    pipeline.add(queue_jpeg)
    pipeline.add(nvvidconv)
    pipeline.add(jpeg_enc)
    pipeline.add(appsink)

    pipeline.add(queue_stream)
    pipeline.add(videoconvert_stream)
    pipeline.add(autovideosink)

    source.link(filter)
    filter.link(tee)
    queue_stream.link(videoconvert_stream)
    videoconvert_stream.link(autovideosink)
    queue_jpeg.link(nvvidconv)
    nvvidconv.link(jpeg_enc)
    jpeg_enc.link(appsink)
    tee.link(queue_jpeg)
    tee.link(queue_stream)

    # pipeline = Gst.parse_launch(
    #     'nvarguscamerasrc sensor_id=0 tnr-strength=1 tnr-mode=2 ee-strength=0 ! video/x-raw(memory:NVMM),width=1280, height=720, framerate=120/1, format=NV12 ! tee name=t ! queue ! videoconvert ! autovideosink t. ! queue ! nvvidconv flip-method=0 ! jpegenc ! appsink emit-signals=True sync=false drop=true ')
    pipeline.set_state(Gst.State.PLAYING)
    # appsink = pipeline.get_by_name("appsink0")
    appsink.connect("new-sample", on_buffer, None)

    while True:
        sleep(0.1)
        if keyboard.is_pressed('p'):
            start_time = time()
            # sample = appsink.emit("pull-sample")
            # array = to_bytes(sample)
            # print(array)
            print('\noh snap')
            #     sample = appsink.pull_sample()
            #     data = to_bytes(sample)
            filename = f'/home/nano/Pictures/{uuid.uuid4()}.jpg'
            f = open(filename, 'wb')
            f.write(array)
            f.close
            end_time = time()
            print(f'time taken: {end_time - start_time}')
        if keyboard.is_pressed('q'):
            print(" from qute")
            break

    pipeline.set_state(Gst.State.NULL)
    main_loop.quit()
