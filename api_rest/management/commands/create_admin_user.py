from django.core.management.base import BaseCommand, CommandError
from api_rest.models import User


class Command(BaseCommand):
    help = 'Cria um novo usuário administrador ou promove um usuário existente a administrador'

    def add_arguments(self, parser):
        parser.add_argument(
            'user_nickname',
            type=str,
            help='Nickname do usuário',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='',
            help='Email do usuário (obrigatório para novo usuário)',
        )
        parser.add_argument(
            '--name',
            type=str,
            default='',
            help='Nome do usuário (obrigatório para novo usuário)',
        )
        parser.add_argument(
            '--age',
            type=int,
            default=0,
            help='Idade do usuário',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='',
            help='Senha do usuário (obrigatória para novo usuário)',
        )

    def handle(self, *args, **options):
        nickname = options['user_nickname']
        
        try:
            user = User.objects.get(user_nickname=nickname)
            # Usuário já existe, apenas promover a admin
            user.is_admin = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Usuário "{nickname}" promovido a administrador.')
            )
        except User.DoesNotExist:
            # Criar novo usuário admin
            email = options['email']
            name = options['name']
            password = options['password']
            age = options['age']

            if not email or not name or not password:
                raise CommandError(
                    'Para criar um novo usuário, forneça --email, --name e --password'
                )

            user = User(
                user_nickname=nickname,
                user_name=name,
                user_email=email,
                user_age=age,
                is_admin=True,
            )
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Usuário administrador "{nickname}" criado com sucesso.'
                )
            )
