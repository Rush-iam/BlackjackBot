from alembic import command
from alembic.config import Config as AlembicConfig
from alembic.util import exc


def test_downgrades(alembic_cfg: AlembicConfig):
    command.downgrade(alembic_cfg, 'base')

    while True:
        try:
            command.upgrade(alembic_cfg, '+1')
        except exc.CommandError:
            print('DONE!')
            break
        command.downgrade(alembic_cfg, '-1')
        command.upgrade(alembic_cfg, '+1')

        print('SUCCESS: ', end='')
        command.current(alembic_cfg)
