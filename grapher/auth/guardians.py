from datetime import datetime, timedelta

from flask_oauthlib.provider import OAuth2Provider
from passlib.apps import custom_app_context as pwd_context

from . import resources
from .. import settings

oauth = OAuth2Provider()

grants = resources.Grant()
tokens = resources.Token()
grant_owner = resources.GrantOwner()
client_grants = resources.ClientGrants()


@oauth.grantgetter
def load_grant(client_id, code):
    for grant in client_grants.manager.match(origin=client_id).values():
        if grant['code'] == code:
            return grant


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    expires_at = datetime.utcnow() + timedelta(
            seconds=settings.effective.AUTH['grant']['expires_in_seconds'])

    grant = dict(
            code=code['code'],
            redirect_uri=request.redirect_uri,
            scopes=request.scopes,
            expires_at=expires_at
    )

    grants_created, failed = grants.manager.create({0: grant})

    client_grant = {'_origin': client_id,
                    '_target': grants_created[0][grants.manager.identity]}

    client_grants.manager.create({0: client_grant}, raise_errors=True)

    return grants_created[0]


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return tokens.manager.query({'access_token': access_token}, limit=1)
    elif refresh_token:
        return tokens.manager.query({'refresh_token': access_token}, limit=1)


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    existing_tokens = tokens.manager.query(
            client_id=request.client.client_id,
            user_id=request.user.id)

    tokens.manager.delete(existing_tokens)

    expires = datetime.utcnow() + timedelta(seconds=token.get('expires_in'))

    token = dict(
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            token_type=token['token_type'],
            _scopes=token['scope'],
            expires=expires,
            client_id=request.client.client_id,
            user_id=request.user.id,
    )

    created, failed = tokens.manager.create({0: token})

    return created[0]


class Guardian:
    @classmethod
    def check_permissions(cls, resource):
        pass

    @classmethod
    def hash(cls, password):
        return pwd_context.encrypt(password)

    @classmethod
    def verify(cls, password, hashed_password):
        return pwd_context.verify(password, hashed_password)
