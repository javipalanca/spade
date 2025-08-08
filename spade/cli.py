import sys
import click
import spade
import socket

from pyjabber.server import Server
from pyjabber.server_parameters import Parameters
from rich.console import Console
from rich.panel import Panel
from loguru import logger


def check_port_in_use(port, host="0.0.0.0"):
    """Checks if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex((host, port))
        return result == 0


def create_cli():
    """Factory function to create the CLI"""

    @click.group()
    def cli():
        """SPADE command line tool"""
        pass

    @cli.command()
    @click.option("--host", default="0.0.0.0", help="Server host")
    @click.option("--client_port", default=5222, help="Client port")
    @click.option("--server_port", default=5269, help="Server port")
    @click.option("--debug", is_flag=True, default=False, help="Enables debug mode")
    @click.option("--timeout", default=600, help="Connection timeout")
    @click.option(
        "--db",
        type=str,
        default="server.db",
        show_default=True,
        help="Path for database file",
    )
    @click.option(
        "--purge",
        is_flag=True,
        default=False,
        help="Restore database file to default state (empty)",
    )
    @click.option(
        "--memory", is_flag=True, default=False, help="Use an in-memory database"
    )
    def run(host, client_port, server_port, debug, timeout, db, purge, memory):
        """Launch an XMPP server"""
        if check_port_in_use(client_port, host):
            click.echo(f"Error: The port {client_port} is already in use.")
            sys.exit(1)
        if check_port_in_use(server_port, host):
            click.echo(f"Error: The port {server_port} is already in use.")
            sys.exit(1)

        logger.remove()
        if debug:
            level = "DEBUG"
        else:
            level = "INFO"

        logger.add(
            sys.stderr,
            enqueue=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - <level>{level}: {message}</level>",
            level=level,
        )

        server = Server(
            Parameters(
                host=host,
                client_port=client_port,
                server_port=server_port,
                connection_timeout=timeout,
                database_path=db,
                database_purge=purge,
                database_in_memory=memory,
            )
        )

        print_spade_info()
        container = spade.container.Container()
        loop = container.loop
        loop.run_until_complete(server.start())

    def print_spade_info():
        """Prints SPADE information"""

        console = Console()

        project_name = "[bold green]SPADE[/bold green] - [yellow]Smart Python Agent Development Environment[/yellow]"
        author = (
            "[green]Development Lead:[/green]\n"
            "  - [cyan]Javi Palanca[/cyan]\n"
            "[green]Funded by:[/green]\n"
            "  - [cyan]Valencian Research Institute for Artificial Intelligence (VRAIN)[/cyan]\n"
            "[green]URL:[/green]\n"
            "  - [cyan] https://spadeagents.eu[/cyan]\n"
            "[green]Documentation:[/green]\n"
            "  - [cyan] http://spade-mas.readthedocs.io/[/cyan]"
        )

        footer = f"[cyan]Version:[/cyan] {spade.__version__}   [magenta]License:[/magenta] MIT"

        console.print(
            Panel.fit(
                f"{project_name}\n\n{author}",
                title="SPADE",
                subtitle=footer,
                border_style="blue",
            )
        )

    @cli.command()
    def version():
        """Displays the SPADE version"""
        click.echo(spade.__version__)

    return cli


# Create a single instance of the CLI
cli = create_cli()

if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
