def test_active_stage_and_analog_blocks_import_without_cycle():
    from photonx_eda_pcb.active_stages import detect_opamp_comparator_stages
    from photonx_eda_pcb.analog_blocks import detect_analog_blocks, AnalogBlockCandidate
    assert callable(detect_opamp_comparator_stages)
    assert callable(detect_analog_blocks)
    assert AnalogBlockCandidate.__name__=="AnalogBlockCandidate"
