import sys
import click
import spade
import socket
from pyjabber.server import Server

def check_port_in_use(port, host='0.0.0.0'):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

def create_cli():
    """Factory function to create the CLI"""
    @click.group()
    def cli():
        """SPADE command line tool"""
        pass

    @cli.command()
    @click.option('--host', default='0.0.0.0', help='Server host')
    @click.option('--client_port', default=5222, help='Client port')
    @click.option('--server_port', default=5269, help='Server port')
    @click.option('--debug', is_flag=True, default=False, help='Enables debug mode')
    def run(host, client_port, server_port, debug):
        """Launch an XMPP server"""
        if check_port_in_use(client_port, host):
            click.echo(f"Error: The port {client_port} is already in use.")
            sys.exit(1)
        if check_port_in_use(server_port, host):
            click.echo(f"Error: The port {server_port} is already in use.")
            sys.exit(1)

        server = Server(host=host, client_port=client_port, 
                        server_port=server_port, 
                        connection_timeout=600)
        server.start(debug=debug)

    @cli.command()
    def version():
        """Displays the SPADE version"""
        click.echo(spade.__version__)

    return cli

# Create a single instance of the CLI
cli = create_cli()

if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover