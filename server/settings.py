import os
import logging

NONCE = os.getenv("NONCE_KEY", "s+x(+u$nx^12+x#pgk&g48ctuf*(ibz)h2v!uq)*_=1h(5wwae")
SECRET_KEY = os.getenv("NONCE_KEY", "x:T9(S.6RyKL-=gf3$XPw(>_")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)
