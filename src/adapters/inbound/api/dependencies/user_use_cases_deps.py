from src.adapters.inbound.api.dependencies.repo_deps import UserRepoDep
from src.adapters.inbound.api.dependencies.security_deps import (
    HasherDep,
    TokenHandlerDep,
)
from src.application.use_cases.user.user_auth import UserAuthUseCase
from src.application.use_cases.user.user_create import UserCreateUseCase
from src.application.use_cases.user.user_login import UserLoginUseCase


def user_create_use_case(
    user_repo: UserRepoDep,
    hasher: HasherDep,
) -> UserCreateUseCase:
    return UserCreateUseCase(user_repo=user_repo, hasher=hasher)


def user_login_use_case(
    user_repo: UserRepoDep,
    hasher: HasherDep,
    token_handler: TokenHandlerDep,
) -> UserLoginUseCase:
    return UserLoginUseCase(
        user_repo=user_repo, hasher=hasher, token_handler=token_handler
    )


def user_auth_use_case(
    user_repo: UserRepoDep,
    token_handler: TokenHandlerDep,
) -> UserAuthUseCase:
    return UserAuthUseCase(user_repo=user_repo, token_handler=token_handler)
