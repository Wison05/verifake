def run_video_stage1_preprocess(*args, **kwargs):
    from services.ai.pipelines.video_stage1.preprocess import (
        run_video_stage1_preprocess as _run_video_stage1_preprocess,
    )

    return _run_video_stage1_preprocess(*args, **kwargs)

__all__ = ["run_video_stage1_preprocess"]
