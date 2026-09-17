from photonx_eda_pcb.pipeline_stages.context import PipelineContext
from photonx_eda_pcb.pipeline_stages.stage import Stage
from photonx_eda_pcb.pipeline_stages.discovery import discovery_stage
from photonx_eda_pcb.pipeline_stages.parsing import parsing_stage
from photonx_eda_pcb.pipeline_stages.runner import run_pipeline

def test_discovery_and_parsing_pipeline():
    ctx=PipelineContext(inputs={'files':['b','a'],'parser':lambda x:x.upper()})
    stages=[Stage('discovery',discovery_stage,provides=('discovered_files',)),Stage('parsing',parsing_stage,requires=('discovered_files',),provides=('parsed_inputs',))]
    run_pipeline(ctx,stages)
    assert ctx.get('discovered_files')==['a','b']
    assert ctx.get('parsed_inputs')==['A','B']
