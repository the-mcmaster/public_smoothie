# Smoothie Arch Boot

The point of this respository is to create a custom arch iso image boot based of the releng archiso profile. This image includes specific packages needed for the **smoothie-processing-server** installer respository.

## Added Packages

- git
- python-pip

## Creating Fresh Image

The install process assumes that it is working on an arch system.

1. Clone the respository

`git clone https://github.com/the-mcmaster/smoothie-arch-iso.git`

2. Make sure to have the arch package **archiso** installed and updated on the system.

`doas pacman -S archiso`

3. Execute the sync script make the custom arch iso file in `path_to_repo/out_dir`

`doas bash path_to_repo/sync.sh`

After the script finishes, the newly created ISO file will be located in `path_to_repo/out_dir`.

## Extra Notes

- In the sync.sh file, it executes the command `mkarchiso`. This command will mount files on the computer. If interrupted, these mounts will not be unmounted. This causes issues when removing certain directories. Un-mounting these directories solves these problems.
- This problem is solved after a reboot.
