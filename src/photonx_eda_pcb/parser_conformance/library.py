from .model import ConformanceCase,ConformanceExpectation
def builtin_cases():
    return [
        ConformanceCase("gerber-linear","gerber","%FSLAX24Y24*%\n%MOMM*%\n%ADD10C,0.200*%\nD10*\nX000000Y000000D02*\nX010000Y000000D01*\nM02*\n",ConformanceExpectation({"tracks":1,"pads":0,"outline":0})),
        ConformanceCase("gerber-incremental-linear","gerber","%FSLIX24Y24*%\n%MOMM*%\n%ADD10C,0.200*%\nD10*\nX010000Y000000D02*\nX010000Y000000D01*\nM02*\n",ConformanceExpectation({"tracks":1,"pads":0,"outline":0})),
        ConformanceCase("gerber-flash","gerber","%FSLAX24Y24*%\n%MOMM*%\n%ADD10C,1.000*%\nD10*\nX010000Y020000D03*\nM02*\n",ConformanceExpectation({"tracks":0,"pads":1,"outline":0})),
        ConformanceCase("gerber-center-line-macro-flash","gerber","%FSLAX24Y24*%\n%MOMM*%\n%AMBOX*21,1,$1,$2,0,0,0*%\n%ADD10BOX,1.0X2.0*%\nD10*\nX010000Y020000D03*\nM02*\n",ConformanceExpectation({"tracks":0,"pads":1,"outline":0})),
        ConformanceCase("gerber-lower-left-line-macro-flash","gerber","%FSLAX24Y24*%\n%MOMM*%\n%AMLLBOX*22,1,$1,$2,-$1/2,-$2/2,0*%\n%ADD10LLBOX,2.0X1.0*%\nD10*\nX010000Y020000D03*\nM02*\n",ConformanceExpectation({"tracks":0,"pads":1,"outline":0})),
        ConformanceCase("gerber-g75-ccw-arc","gerber","%FSLAX24Y24*%\n%MOMM*%\n%ADD10C,0.200*%\nD10*\nG75*\nX010000Y000000D02*\nG03X000000Y010000I-010000J000000D01*\nM02*\n",ConformanceExpectation({"tracks":8,"pads":0,"outline":0})),
        ConformanceCase("gerber-g74-ccw-quarter-arc","gerber","%FSLAX24Y24*%\n%MOMM*%\n%ADD10C,0.200*%\nD10*\nG74*\nX110000Y060000D02*\nG03X070000Y100000I040000J000000D01*\nM02*\n",ConformanceExpectation({"tracks":16,"pads":0,"outline":0})),
        ConformanceCase("gerber-region-strict","gerber","%FSLAX24Y24*%\n%MOMM*%\nG36*\nM02*\n",ConformanceExpectation(exception_type="UnsupportedFeatureError")),
        ConformanceCase("gerber-region-permissive","gerber","%FSLAX24Y24*%\n%MOMM*%\nG36*\nM02*\n",ConformanceExpectation({"tracks":0,"pads":0,"outline":0},("UNSUPPORTED_GERBER_CONSTRUCT",)),strict=False),
        ConformanceCase("excellon-basic","excellon","M48\nMETRIC\nT01C0.800\n%\nT01\nX1.000Y1.000\nX2.000Y2.000\nM30\n",ConformanceExpectation({"drills":2,"slots":0,"routes":0})),
        ConformanceCase("excellon-g85-slot","excellon","M48\nMETRIC\nT01C0.800\n%\nT01\nX1.000Y2.000G85X3.000Y2.000\nM30\n",ConformanceExpectation({"drills":0,"slots":1,"routes":0})),
        ConformanceCase("excellon-linear-route","excellon","M48\nMETRIC\nT01C0.800\n%\nT01\nG00X1.000Y1.000\nM15\nG01X2.000Y1.000\nM16\nM30\n",ConformanceExpectation({"drills":0,"slots":0,"routes":1})),
        ConformanceCase("excellon-ij-route-arc","excellon","M48\nMETRIC\nT01C0.800\n%\nT01\nG00X10.000Y0.000\nM15\nG03X0.000Y10.000I-10.000J0.000\nM16\nM30\n",ConformanceExpectation({"drills":0,"slots":0,"routes":1})),
        ConformanceCase("excellon-radius-route-arc","excellon","M48\nMETRIC\nT01C0.800\n%\nT01\nG00X10.000Y0.000\nM15\nG03X0.000Y10.000A10.000\nM16\nM30\n",ConformanceExpectation({"drills":0,"slots":0,"routes":1})),
    ]
