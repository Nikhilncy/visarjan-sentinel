"""Visarjan Sentinel: evidence-backed ghat prioritisation for Bhopal Municipal Corporation.

Deterministic pipeline: CSV readings -> expected grid -> CPCB Class B status
per reading -> ranked ghats with plain-words reasons -> briefs.
No model sits in the scoring path.
"""

__version__ = "0.1.0"
