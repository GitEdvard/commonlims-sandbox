import click


@click.group()
@click.pass_context
def cli(ctx):
    from sentry.runner import configure
    configure()


@cli.command("add-project-for-example-import")
@click.argument("project_name")
def add_project(project_name):
    from sentry_plugins.snpseq.plugin.models import Project
    from sentry.models.organization import Organization
    from clims.services.application import ioc, ApplicationService
    from clims.models.plugin_registration import PluginRegistration
    org = Organization.objects.get(name="lab")
    app = ApplicationService()
    ioc.set_application(app)
    snpseq_plugin, _ = PluginRegistration.objects.get_or_create(
        name="clims_snpseq_plugins.snpseq.plugin.SnpSeqPlugin", version='1.0.0', organization=org)
    app.extensibles.register(snpseq_plugin, Project)
    new_project = Project(name=project_name, organization=org)
    new_project.save()


def cli_main():
    cli(obj={})


if __name__ == "__main__":
    cli_main()
