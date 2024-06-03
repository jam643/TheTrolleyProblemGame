from utils import math
from utils.pgutils import pgutils
import pytest
import numpy as np


@pytest.fixture
def sim_to_real():
    """
                       x▲
                        │
     ▲                  │  y-axis flipped
    y│                  │
     │                  └─────────►
     │                  Screen    y
     │
     │
     └───────────►
     Real        x
    """
    return pgutils.SimToReal(
        pgutils.SimToReal.Params(
            pxl_per_meter=40,
            screen_ref_frame_rel_real=math.Pose(x=2, y=1, theta=np.pi / 2),
            fps=60,
            sim_time_rel_real=2,
        )
    )


def test_sim_to_real_transform(sim_to_real):
    # Point at origin of real-world reference frame
    vec_rel_real = np.vstack([0, 0, 0])
    vec_rel_sim = sim_to_real.get_sim_from_real(vec_rel_real)
    assert np.allclose(
        vec_rel_sim,
        np.vstack(
            [
                -1 * sim_to_real.params.pxl_per_meter,
                -2 * sim_to_real.params.pxl_per_meter,
                -np.pi / 2,
            ]
        ),
    )

    # Point at origin of sim reference frame
    vec_rel_real = np.vstack([2, 1, np.pi / 2])
    vec_rel_sim = sim_to_real.get_sim_from_real(vec_rel_real)
    assert np.allclose(
        vec_rel_sim,
        np.vstack([0, 0, 0]),
    )


def test_real_to_sim_transform(sim_to_real):
    # Point at origin of sim reference frame
    vec_rel_sim = np.vstack([0, 0, 0])
    vec_rel_real = sim_to_real.get_real_from_sim(vec_rel_sim)
    assert np.allclose(
        vec_rel_real,
        np.vstack([2, 1, np.pi / 2]),
    )

    # Point at origin of real-world reference frame
    vec_rel_sim = np.vstack(
        [
            -1 * sim_to_real.params.pxl_per_meter,
            -2 * sim_to_real.params.pxl_per_meter,
            -np.pi / 2,
        ]
    )
    vec_rel_real = sim_to_real.get_real_from_sim(vec_rel_sim)
    assert np.allclose(
        vec_rel_real,
        np.vstack([0, 0, 0]),
    )


def test_sim_to_real_and_back_transform(sim_to_real):
    vec_rel_real = np.random.random((3, 1))
    vec_rel_sim = sim_to_real.get_sim_from_real(vec_rel_real)
    vec_rel_real_back = sim_to_real.get_real_from_sim(vec_rel_sim)
    assert np.allclose(vec_rel_real, vec_rel_real_back)
