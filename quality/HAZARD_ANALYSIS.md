# Hazard Analysis

Research Use Only. MEM is a computational research framework and is not validated for clinical diagnosis, treatment selection, molecular profiling, clonal lineage reconstruction, or minimal/measurable residual disease reporting.

## Hazardous situations (research program, not clinical use)
| Hazard | Hazardous situation | Harm |
| Unverified public image | Used as if licensed and patient-linked | Invalid thesis/journal claims; possible license violation |
| Split leakage | Test morphology seen in training | Inflated metrics presented as generalization |
| Prohibited wording | Report says an unsupported MRD or genomic-clone claim | Reader believes a clinical or molecular result exists |
| Identifier-like metadata | File names or EXIF contain fake or real identifiers | Privacy incident if real; process failure if fake is missed |
| Untrusted checkpoint | Pickle executed | Code execution |
| Demo UI | Looks like a diagnostic product | User overtrust / automation bias |
| Topology output | Never interpret topology as phylogeny | False biological narrative |

## Controls
Prevention, detection, and fail-closed stop. See the control-evidence matrix.
