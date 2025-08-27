"""A HeuDiConv heuristic for the EF dataset."""

from __future__ import annotations
from typing import Optional

from heudiconv.utils import SeqInfo


def create_key(
    template: Optional[str],
    outtype: tuple[str, ...] = ("nii.gz",),
    annotation_classes: None = None,
) -> tuple[str, tuple[str, ...], None]:
    if template is None or not template:
        raise ValueError("Template must be a valid format string")
    return (template, outtype, annotation_classes)


def infotodict(seqinfo: list[SeqInfo]) -> dict[tuple[str, tuple[str, ...], None], list]:
    """Heuristic evaluator for determining which runs belong where.

    This function organizes the image sequence info and organizes it into a
    structured dictionary that maps scan types to series ID based on meta-data.
    Each key corresponds to a different type of image.
    """
    outdicom = ("dicom", "nii.gz")

    # Define the different modalities with their BIDS keys
    t1_norm = create_key(
        "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_run-{item:02d}_rec-norm_T1w",
        outtype=outdicom,
    )
    t2 = create_key(
        "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_run-{item:02d}_T2w",
        outtype=outdicom,
    )
    t2_norm = create_key(
        "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_run-{item:02d}_rec-norm_T2w",
        outtype=outdicom,
    )
    dwi = create_key(
        "{bids_subject_session_dir}/dwi/{bids_subject_session_prefix}_run-{item:02d}_dwi",
        outtype=outdicom,
    )
    asl = create_key(
        "{bids_subject_session_dir}/perf/{bids_subject_session_prefix}_run-{item:02d}_asl",
        outtype=outdicom,
    )
    asl_m0 = create_key(
        "{bids_subject_session_dir}/perf/{bids_subject_session_prefix}_run-{item:02d}_m0scan",
        outtype=outdicom,
    )
    qsm = create_key(
        "{bids_subject_session_dir}/swi/{bids_subject_session_prefix}_run-{item:02d}_qsm",
        outtype=outdicom,
    )
    func_nback = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-nback_run-{item:02d}_bold",
        outtype=outdicom,
    )
    func_rest = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-rest_run-{item:02d}_bold",
        outtype=outdicom,
    )
    dwi_fmap_ap = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-dwi_dir-AP_run-{item:02d}_epi",
        outtype=outdicom,
    )
    dwi_fmap_pa = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-dwi_dir-PA_run-{item:02d}_epi",
        outtype=outdicom,
    )
    fmri_fmap_ap = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-fmri_dir-AP_run-{item:02d}_epi",
        outtype=outdicom,
    )
    fmri_fmap_pa = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-fmri_dir-PA_run-{item:02d}_epi",
        outtype=outdicom,
    )

    # Dictionary to store the sequence info
    # The keys in the dictionary are tuples, the values are each a list that
    # holds the series IDs corresponding to each image modality.
    info: dict[tuple[str, tuple[str, ...], None], list] = {
        t1_norm: [],
        t2: [],
        t2_norm: [],
        dwi_fmap_ap: [],
        dwi_fmap_pa: [],
        dwi: [],
        fmri_fmap_ap: [],
        fmri_fmap_pa: [],
        func_nback: [],
        func_rest: [],
        asl: [],
        asl_m0: [],
        qsm: [],
    }

    # Loop through sequences and categorize them based on properties
    for s in seqinfo:
        # T1-weighted scans
        if (
            ("anat_t1w" in s.protocol_name) or
            ("anat_T1w" in s.protocol_name) or
            ("ABCD_T1w_MPR_vNav" in s.protocol_name)) and (
            ("setter" not in s.protocol_name)
            and (s.dim1 == 256)
            and (s.dim2 == 256)
            and ((s.dim3 == 352) or (s.dim3 == 176))
        ):
            # if not s.is_motion_corrected:
            # assigning directly rather than appending updates the list with
            # the most recent/correct scan
            info[t1_norm].append(s.series_id)

        # T2-weighted scans
        elif (
            ("anat_t2w" in s.protocol_name) or
            ("anat_T2w" in s.protocol_name) or
            ("ABCD_T2w_SPC_vNav" in s.protocol_name)) and (
            ("setter" not in s.protocol_name)
            and (s.dim1 == 256)
            and (s.dim2 == 256)
            and ((s.dim3 == 352) or (s.dim3 == 176))
        ):
            if "NORM" in s.image_type:
                info[t2_norm].append(s.series_id)
            else:
                info[t2].append(s.series_id)


        # Diffusion scans
        elif (
            (s.protocol_name == "dwi_acq-multishell_dir-AP_dwi") or
            (s.protocol_name == "ABCD_dMRI")
            and (s.dim1 == 140)
            and (s.dim2 == 140)
            and (s.dim3 == 81)
        ):
            info[dwi].append(s.series_id)

        # distortion map, anterior to posterior
        elif (
            (s.protocol_name == "fmap_acq-dMRIdistmap_dir-AP_epi") or
            (s.protocol_name == "ABCD_dMRI_DistortionMap_AP")
        ):
            info[dwi_fmap_ap].append(s.series_id)

        # distortion map, posterior to anterior
        elif (
            (s.protocol_name == "fmap_acq-dMRIdistmap_dir-PA_epi") or
            (s.protocol_name == "ABCD_dMRI_DistortionMap_PA")
        ):
            info[dwi_fmap_pa].append(s.series_id)

        # Resting-state functional scans
        elif (
            ("rest" in s.protocol_name)
            and (s.dim1 == 90)
            and (s.dim2 == 90)
            and (s.dim3 == 60)
        ):
            info[func_rest].append(s.series_id)

        # N-back functional scans
        elif (
            ("fracnoback" in s.protocol_name) or
            ("frac-no-back" in s.protocol_name)
            and (s.dim1 == 90)
            and (s.dim2 == 90)
            and (s.dim3 == 60)
        ):
            info[func_nback].append(s.series_id)

        # fMRI distortion maps
        # distortion map, anterior to posterior
        elif s.protocol_name in ("ABCD_fMRI_DistortionMap_AP", "fmap_acq-fMRIdistmap_dir-AP_epi"):
            info[fmri_fmap_ap].append(s.series_id)

        # distortion map, posterior to anterior
        elif s.protocol_name in ("ABCD_fMRI_DistortionMap_PA", "fmap_acq-fMRIdistmap_dir-PA_epi"):
            info[fmri_fmap_pa].append(s.series_id)

        # ASL
        elif (
            (s.series_description == "asl_acq-3dspiralv20unbalanced_asl_ASL") or
            (s.series_description == "ASL_3DSPIRAL_V20_GE_UnBalanced_ASL")
        ):
            info[asl].append(s.series_id)

        # ASL M0 scan
        elif (
            (s.series_description == "asl_acq-3dspiralv20unbalanced_asl_M0") or
            (s.series_description == "ASL_3DSPIRAL_V20_GE_UnBalanced_M0")
        ):
            info[asl_m0].append(s.series_id)

        # QSM
        elif (
            (s.protocol_name == "qsm_acq-1.5mm_GRE") or
            (('QSM_SWI' in s.protocol_name) and
            (s.dim1 == 160) and
            (s.dim2 == 120) and (s.dim3 == 384))
        ):
            info[qsm].append(s.series_id)

    return info
