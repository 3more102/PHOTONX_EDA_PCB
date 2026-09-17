from photonx_eda_pcb.parsers.common.checksum import crc32_text
def test_crc_is_stable(): assert crc32_text('abc')==crc32_text('abc') and len(crc32_text('abc'))==8
