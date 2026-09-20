from photonx_eda_pcb.kicad_reader.board_reader import read_kicad_board_text
def test_reader():
    d=read_kicad_board_text('(kicad_pcb (net 1 GND) (segment (start 0 0) (end 1 0) (width 0.25) (layer F.Cu) (net 1)) (gr_line (start 0 0) (end 1 0) (layer Edge.Cuts)))'); assert len(d['nets'])==1; assert len(d['segments'])==1; assert len(d['edge_lines'])==1; assert len(d['edge_graphics'])==1



def test_reader_exposes_footprint_copper_graphics():
    d = read_kicad_board_text(
        """
        (kicad_pcb
          (footprint "PHOTONX:RecoveredPad"
            (layer "F.Cu")
            (at 0 0)
            (property "Reference" "P1"
              (layer "F.SilkS")
            )
            (fp_line
              (start 0 0)
              (end 1 0)
              (stroke (width 0.2) (type default))
              (layer "F.Cu")
              (uuid 00000000-0000-0000-0000-000000000094)
            )
          )
        )
        """
    )
    assert d["footprints"][0]["unexpected_copper_graphics"] == [
        {
            "type": "fp_line",
            "layer": "F.Cu",
            "uuid": "00000000-0000-0000-0000-000000000094",
            "child_index": 3,
        }
    ]



def test_reader_exposes_board_fabrication_settings():
    d = read_kicad_board_text(
        """
        (kicad_pcb
          (general (thickness 1.6))
          (setup (pad_to_mask_clearance 0.15))
        )
        """
    )
    assert d["board_settings"] == {
        "thickness": 1.6,
        "pad_to_mask_clearance": 0.15,
        "solder_mask_min_width": None,
        "pad_to_paste_clearance": None,
        "pad_to_paste_clearance_ratio": None,
        "stackup_present": False,
    }



def test_reader_exposes_footprint_and_pad_copper_overrides():
    d = read_kicad_board_text(
        """
        (kicad_pcb
          (footprint "PHOTONX:RecoveredPad"
            (layer "F.Cu")
            (at 0 0)
            (property "Reference" "P1"
              (layer "F.SilkS")
            )
            (clearance 0.2)
            (zone_connect 2)
            (thermal_width 0.3)
            (thermal_gap 0.4)
            (pad "1" smd rect
              (at 0 0)
              (size 1 1)
              (layers "F.Cu")
              (clearance 0.1)
              (zone_connect 1)
              (thermal_width 0.25)
              (thermal_gap 0.35)
              (remove_unused_layer)
              (keep_end_layers)
            )
          )
        )
        """
    )
    footprint = d["footprints"][0]
    assert footprint["copper_overrides"] == {
        "clearance": 0.2,
        "zone_connect": 2,
        "thermal_width": 0.3,
        "thermal_gap": 0.4,
    }
    assert footprint["pads"][0]["copper_overrides"] == {
        "clearance": 0.1,
        "zone_connect": 1,
        "thermal_width": 0.25,
        "thermal_gap": 0.35,
        "remove_unused_layer": True,
        "keep_end_layers": True,
    }


def test_reader_preserves_footprint_net_tie_pad_groups():
    d = read_kicad_board_text(
        """
        (kicad_pcb
          (footprint "PHOTONX:RecoveredPad"
            (layer "F.Cu")
            (at 0 0)
            (uuid 00000000-0000-0000-0000-000000000091)
            (property "Reference" "P1")
            (net_tie_pad_groups "1,2" "3,4")
          )
        )
        """
    )

    assert d["footprints"][0]["net_tie_pad_groups"] == ("1,2", "3,4")
