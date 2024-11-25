import torch
from lightning.pytorch.cli import LightningCLI
from omegaconf import OmegaConf
import wandb
from deepwaters.data import DeepwatersDataModule
from deepwaters.training import define_wandb_metrics


class DeepwatersCLI(LightningCLI):
    def add_arguments_to_parser(self, parser):
        parser.add_argument("--scenario", default="N/A")


def main() -> None:
    # Use TensorFloat32 datatype
    torch.set_float32_matmul_precision("high")
    # Enable cuDNN auto-tuner
    torch.backends.cudnn.benchmark = True
    # Register resolver to parse length of objects (${len:${x}}) in YAML
    OmegaConf.register_new_resolver("len", len, replace=True)

    cli = DeepwatersCLI(
        datamodule_class=DeepwatersDataModule,
        save_config_callback=None,
        run=False,
        parser_kwargs={"parser_mode": "omegaconf"},
        seed_everything_default=False
    )
    model = cli.model
    dm = cli.datamodule
    config = cli.config

    print(dm.split_stats, dm.variables, sep="\n")

    # Set up W&B
    project = config.trainer.logger.init_args.project
    wandb.init(project=project, config=cli.config.as_dict())
    wandb.watch(model)
    define_wandb_metrics()

    cli.trainer.fit(model, datamodule=dm)


if __name__ == "__main__":
    main()
