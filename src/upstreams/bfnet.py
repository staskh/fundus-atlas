# ABOUTME: BF-Net: cloned at a pinned commit, with weights published as an unversioned Google Drive
# ABOUTME: folder — so the archive this atlas ran is pinned here by its own checksum instead.

from dataclasses import dataclass
from pathlib import Path

from datasets.utils import archives

from .utils import paths, source, weights

CODE = source.Checkout(
    "bfnet",
    "https://github.com/rmaphoh/Learning-AVSegmentation",
    "f7de674efe8e4c4d4ed7291d2d00acd7beec7856",
)

#: Where the folder itself lives, for the page and for anyone repeating this by hand.
FOLDER = "https://drive.google.com/drive/folders/1c_UZaq69RmPZjFvccot6GWqnhx2VzFRs"


@dataclass(frozen=True)
class Published:
    """One archive of weights, as it was served on the day it was fetched.

    :param drive: the file's own identifier inside the folder above.
    :param sha256: what that file was, so a run records something a reader can check. **A Google
        Drive folder carries no version and no checksum of its own**: the authors can replace a
        file in place and nothing would say so. This digest is this repository's own measurement,
        taken on the date below, and a download that does not match it is refused rather than run.
    :param seed: the random seed the folder inside the archive is named for. There is one.
    """

    drive: str
    sha256: str
    folder: str
    seed: int = 42


#: The three archives the folder holds — **one per training dataset, not one per seed**. Each holds
#: a single seed, so BF-Net as published is one model and not the eight-member ensemble AutoMorph
#: built from the same architecture.
PUBLISHED = {
    "DRIVE_AV": Published(
        drive="1cOI2TObv8BL6wtBzSQ5e_zvRGvFeNyek",
        sha256="19ea93738eeadb9f41e502b2a7f7f5470a62b0bc05f1bc8c2abab5a925d37e7b",
        folder="DRIVE_AV/DRIVE_AV_randomseed_42/Discriminator_unet",
    ),
    "HRF-AV": Published(
        drive="1mmlAbG21IkFvtpl1Engvwx4yyDWnA42P",
        sha256="adc67b59b08250343b26137347f877b1f11f3f9b6058d3565529fe05955045ac",
        folder="HRF-AV/HRF-AV_randomseed_42/Discriminator_unet",
    ),
    "LES-AV": Published(
        drive="1C_VfJagS5GDSntIzBVGjmCc6qbOdmPH1",
        sha256="a5ef9eafce7a99b9095fda701aae5011be901150567a195b6b5779f94756b8aa",
        folder="LES-AV/LES-AV_randomseed_42/Discriminator_unet",
    ),
}

#: When each digest above was taken, which is the only thing that dates them.
FETCHED = "2026-09-18"

#: Which archive the benchmark runs. The DRIVE-trained one, because it is the only one of the three
#: that trained on none of the datasets this atlas has built an artery/vein store for: the HRF-AV
#: archive would be in-sample on HRF, and LES-AV on LES-AV.
DEFAULT = "DRIVE_AV"


def archive(trained_on: str = DEFAULT) -> Path:
    """The archive of weights, downloaded once and refused unless it is the one pinned above.

    :raises LookupError: if asked for an archive the folder does not hold.
    """
    return weights.fetch(
        f"https://drive.google.com/uc?id={_published(trained_on).drive}",
        paths.weights("bfnet") / f"{trained_on}.zip",
        _published(trained_on).sha256,
        fetch=_from_drive,
    )


def seed_weights(trained_on: str = DEFAULT) -> list[Path]:
    """The three checkpoints of the published seed: the artery branch, the vein branch, the main."""
    packed = archive(trained_on)
    tree = archives.extract(packed, packed.parent / trained_on)
    found = sorted((tree / _published(trained_on).folder).glob("CP_best_F1_*.pth"))
    if len(found) != 3:
        raise RuntimeError(
            f"expected the three checkpoints of one seed in {tree / _published(trained_on).folder}, "
            f"found {len(found)}"
        )
    return found


def seed_folder(trained_on: str = DEFAULT) -> Path:
    """The one folder the checkpoints sit in, which is how the adapter loads a seed."""
    return seed_weights(trained_on)[0].parent


def architecture() -> object:
    """The repository's own generators.

    Its folder is called `scripts`, which is a name several upstreams here use, so it is bound to a
    name of ours rather than put on ``sys.path``; only `model` is imported, because its siblings
    reach for a training stack nothing here installs.
    """
    return source.package("bfnet_scripts", CODE.obtain() / "scripts", modules=["model"]).model


def provenance(trained_on: str = DEFAULT) -> dict[str, object]:
    """What the run records: the pinned code, and which unversioned archive of weights it ran."""
    published = _published(trained_on)
    return {
        **CODE.provenance(),
        "weights": {
            "folder": FOLDER,
            "archive": f"{trained_on}.zip",
            "sha256": published.sha256,
            "fetched": FETCHED,
            "seed": published.seed,
        },
    }


def _published(trained_on: str) -> Published:
    if trained_on not in PUBLISHED:
        raise LookupError(
            f"{trained_on!r} is not one of the archives the folder holds: "
            f"{', '.join(sorted(PUBLISHED))}"
        )
    return PUBLISHED[trained_on]


def _from_drive(url: str, into: Path) -> None:
    """Google Drive serves a file this size behind a confirmation page, which `gdown` answers."""
    import gdown

    gdown.download(url, str(into), quiet=False)
