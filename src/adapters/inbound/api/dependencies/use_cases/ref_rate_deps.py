from typing import Annotated

from fastapi import Depends

from src.adapters.inbound.api.dependencies.repo_deps import ReferenceRateRepoDep
from src.adapters.inbound.api.dependencies.service_deps import nbp_data_provider_dep
from src.adapters.outbound.external_services.nbp.nbp_data_provider import NBPDataProvider
from src.application.use_cases.reference_rate.update import UpdateReferenceRateUseCase


def update_ref_rate_use_case(
    ref_rate_repo: ReferenceRateRepoDep,
    rate_provider: Annotated[NBPDataProvider, Depends(nbp_data_provider_dep)],
) -> UpdateReferenceRateUseCase:
    return UpdateReferenceRateUseCase(
        reference_rate_repo=ref_rate_repo,
        rate_provider=rate_provider,
    )
