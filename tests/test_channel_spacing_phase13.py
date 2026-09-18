from photonx_eda_pcb.channel_detection.geometry import channel_spacing,regular_spacing
def test_regular_channel_spacing():
    s=channel_spacing([(0,0),(10,0),(20,0)])
    assert regular_spacing(s,.01)
