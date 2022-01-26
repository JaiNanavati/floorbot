
def lower(x):
   if isinstance(x, list):
     return [lower(v) for v in x]
   elif isinstance(x, dict):
     return {k.lower(): lower(v) for k, v in x.items()}
   else:
     return x
