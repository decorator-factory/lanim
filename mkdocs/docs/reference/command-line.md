# Command-line interface reference

## Usage
```
lanim [-?] [-e IDENTIFIER] [-w WIDTH] [-h HEIGHT] [-f FPS] [-t THREADS] [-p PATH] -o PATH [--range PERCENT:PERCENT] module
```

## Arguments

| Argument               | Shorthand | Description                | Default |
| ---------------------- | --------  | -------------------------  | ------- |
| `--help`               | `-?`      | Show the reference         ||
| `--export-name [NAME]` | `-e`      | Name to import from module | `export`|
| `--width [WIDTH]`      | `-w`      | Frame width, in pixels     | 1280    |
| `--height [HEIGHT]`    | `-h`      | Frame height, in pixels    | 720     |
| `--fps [FPS]`          | `-f`      | Frames per second          | 30      |
| `--threads [THREADS]`  | `-t`      | Number of threads to launch| `multiprocessing.cpu_count()` |
| `--temp-dir [PATH]`    | `-p`      | Temporary working directory|`./.lanim`|
| `--output PATH`        | `-o`      | Output file                ||
| `module` (positional)  |           | Module to render, like `lanim.examples.hello` ||

!!! note "`--threads`"
    When you invoke `lanim --help`, the help message will show how many threads
    you have available, e.g.:
    ```
      -t THREADS, --threads THREADS
        Number of threads do launch. Defaults to CPU count (12 in your case)
    ```