#  Copyright (c) ZenML GmbH 2023. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
"""Models representing API keys."""

from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import UUID

from passlib.context import CryptContext
from pydantic import BaseModel, Field

from zenml.models.base_models import (
    WorkspaceScopedRequestModel,
    WorkspaceScopedResponseModel,
    update_model,
)
from zenml.models.constants import STR_FIELD_MAX_LENGTH
from zenml.models.filter_models import WorkspaceScopedFilterModel
from zenml.utils.string_utils import b64_decode, b64_encode

# ---- #
# BASE #
# ---- #


class APIKey(BaseModel):
    """Encoded model for API keys."""

    id: UUID
    key: str

    @classmethod
    def decode_api_key(cls, encoded_key: str) -> "APIKey":
        """Decodes an API key from a base64 string.

        Args:
            encoded_key: The encoded API key.

        Returns:
            The decoded API key.

        Raises:
            ValueError: If the key is not valid.
        """
        try:
            json_key = b64_decode(encoded_key)
            return cls.parse_raw(json_key)
        except Exception:
            raise ValueError("Invalid API key.")

    def encode(self) -> str:
        """Encodes the API key in a base64 string that includes the key ID.

        Returns:
            The encoded API key.
        """
        return b64_encode(self.json())


class APIKeyBaseModel(BaseModel):
    """Base model for API keys."""

    name: str = Field(
        title="The name of the API Key.",
        max_length=STR_FIELD_MAX_LENGTH,
    )

    description: str = Field(
        default="",
        title="The description of the API Key.",
        max_length=STR_FIELD_MAX_LENGTH,
    )


# -------- #
# RESPONSE #
# -------- #


class APIKeyResponseModel(APIKeyBaseModel, WorkspaceScopedResponseModel):
    """Response model for API keys."""

    key: Optional[str] = Field(
        default=None,
        title="The API key. Only set immediately after creation or rotation.",
    )

    active: bool = Field(
        default=True,
        title="Whether the API key is active.",
    )

    retain_period_minutes: int = Field(
        title="Number of minutes for which the previous key is still valid "
        "after it has been rotated.",
    )

    last_used: datetime = Field(
        title="Time when the API key was last used to log in."
    )

    last_rotated: datetime = Field(
        title="Time when the API key was last rotated."
    )

    def set_key(self, key: str) -> None:
        """Sets the API key and encodes it.

        Args:
            key: The API key value to be set.
        """
        self.key = APIKey(id=self.id, key=key).encode()


class APIKeyInternalResponseModel(APIKeyResponseModel):
    """Response model for API keys used internally."""

    previous_key: Optional[str] = Field(
        default=None,
        title="The previous API key. Only set if the key was rotated.",
    )

    def verify_key(
        self,
        key: str,
    ) -> bool:
        """Verifies a given key against the stored (hashed) key(s).

        Args:
            key: Input key to be verified.

        Returns:
            True if the keys match.
        """
        # even when the hashed key is not set, we still want to execute
        # the hash verification to protect against response discrepancy
        # attacks (https://cwe.mitre.org/data/definitions/204.html)
        key_hash: str = ""
        context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        if self.key is not None and self.active:
            key_hash = self.key
        result = context.verify(key, key_hash)

        # same for the previous key, if set and if it's still valid
        key_hash = ""
        if (
            self.previous_key is not None
            and self.active
            and self.retain_period_minutes > 0
        ):
            # check if the previous key is still valid
            if datetime.now() - self.last_rotated < timedelta(
                minutes=self.retain_period_minutes
            ):
                key_hash = self.previous_key
        previous_result = context.verify(key, key_hash)

        return result or previous_result


# ------ #
# FILTER #
# ------ #


class APIKeyFilterModel(WorkspaceScopedFilterModel):
    """Model to enable advanced filtering of API keys."""

    name: Optional[str] = Field(
        default=None,
        description="Name of the API key",
    )
    active: Optional[Union[bool, str]] = Field(
        default=None,
        title="Whether the API key is active.",
    )
    last_used: Optional[Union[datetime, str]] = Field(
        default=None, title="Time when the API key was last used to log in."
    )
    last_rotated: Optional[Union[datetime, str]] = Field(
        default=None, title="Time when the API key was last rotated."
    )
    workspace_id: Optional[Union[UUID, str]] = Field(
        default=None, description="Workspace that the API key belongs to"
    )
    user_id: Optional[Union[UUID, str]] = Field(
        default=None, description="User that created the API key"
    )


# ------- #
# REQUEST #
# ------- #


class APIKeyRequestModel(APIKeyBaseModel, WorkspaceScopedRequestModel):
    """Request model for API keys."""


class APIKeyRotateRequestModel(BaseModel):
    """Request model for API key rotation."""

    retain_period_minutes: int = Field(
        default=0,
        title="Number of minutes for which the previous key is still valid "
        "after it has been rotated.",
    )


# ------- #
# UPDATE  #
# ------- #


@update_model
class APIKeyUpdateModel(APIKeyRequestModel):
    """Update model for API keys."""

    active: Optional[bool] = Field(
        default=True,
        title="Whether the API key is active.",
    )


class APIKeyInternalUpdateModel(APIKeyUpdateModel):
    """Update model for API keys used internally."""

    update_last_used: bool = Field(
        default=False,
        title="Whether to update the last used timestamp.",
    )
