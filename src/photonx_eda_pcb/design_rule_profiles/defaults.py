from .model import RuleProfile
def default_profile(name="generic"):return RuleProfile(str(name))
def conservative_profile():return RuleProfile("conservative",.2,.2,.25,.125,.125)
