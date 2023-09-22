#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
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
"""SQLModel implementation of user tables."""

from datetime import datetime
from secrets import token_hex
from typing import Optional, Tuple
from uuid import UUID

from passlib.context import CryptContext
from sqlmodel import Field, Relationship

from zenml.models import (
    APIKeyInternalResponseModel,
    APIKeyInternalUpdateModel,
    APIKeyRequestModel,
    APIKeyResponseModel,
    APIKeyRotateRequestModel,
    APIKeyUpdateModel,
)
from zenml.zen_stores.schemas.base_schemas import NamedSchema
from zenml.zen_stores.schemas.schema_utils import build_foreign_key_field
from zenml.zen_stores.schemas.user_schemas import UserSchema
from zenml.zen_stores.schemas.workspace_schemas import WorkspaceSchema


class APIKeySchema(NamedSchema, table=True):
    """SQL Model for API keys."""

    __tablename__ = "api_key"

    description: str
    key: str
    previous_key: Optional[str] = Field(default=None, nullable=True)
    retain_period: int = Field(default=0)
    active: bool = Field(default=True)
    last_used: datetime = Field(default_factory=datetime.utcnow)
    last_rotated: datetime = Field(default_factory=datetime.utcnow)

    workspace_id: UUID = build_foreign_key_field(
        source=__tablename__,
        target=WorkspaceSchema.__tablename__,
        source_column="workspace_id",
        target_column="id",
        ondelete="CASCADE",
        nullable=False,
    )
    workspace: "WorkspaceSchema" = Relationship(back_populates="api_keys")

    user_id: UUID = build_foreign_key_field(
        source=__tablename__,
        target=UserSchema.__tablename__,
        source_column="user_id",
        target_column="id",
        ondelete="CASCADE",
        nullable=False,
    )
    user: "UserSchema" = Relationship(back_populates="api_keys")

    @classmethod
    def _generate_jwt_secret_key(cls) -> str:
        """Generate a random API key.

        Returns:
            A random API key.
        """
        return token_hex(32)

    @classmethod
    def _get_hashed_key(cls, key: str) -> str:
        """Hashes the input key and returns the hash value.

        Args:
            key: The key value to hash.

        Returns:
            The key hash value.
        """
        context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return context.hash(key)

    @classmethod
    def from_request(
        cls,
        request: APIKeyRequestModel,
    ) -> Tuple["APIKeySchema", str]:
        """Convert a `APIKeyRequestModel` to a `APIKeySchema`.

        Args:
            request: The request model to convert.

        Returns:
            The converted schema and the un-hashed API key.
        """
        key = cls._generate_jwt_secret_key()
        hashed_key = cls._get_hashed_key(key)
        now = datetime.utcnow()
        return (
            cls(
                name=request.name,
                description=request.description,
                key=hashed_key,
                workspace_id=request.workspace,
                user_id=request.user,
                created=now,
                updated=now,
                last_used=now,
                last_rotated=now,
            ),
            key,
        )

    def to_model(
        self,
    ) -> APIKeyResponseModel:
        """Convert a `APIKeySchema` to an `APIKeyModel`.

        Returns:
            The created APIKeyModel.
        """
        return APIKeyResponseModel(
            id=self.id,
            name=self.name,
            description=self.description,
            workspace=self.workspace.to_model(),
            user=self.user.to_model(True) if self.user else None,
            created=self.created,
            updated=self.updated,
            last_used=self.last_used,
            last_rotated=self.last_rotated,
            retain_period_minutes=self.retain_period,
            active=self.active,
        )

    def to_internal_model(
        self,
    ) -> APIKeyInternalResponseModel:
        """Convert a `APIKeySchema` to an `APIKeyInternalResponseModel`.

        The internal response model includes the hashed key values.

        Returns:
            The created APIKeyInternalResponseModel.
        """
        return APIKeyInternalResponseModel(
            id=self.id,
            name=self.name,
            description=self.description,
            key=self.key,
            previous_key=self.previous_key,
            workspace=self.workspace.to_model(),
            user=self.user.to_model(True) if self.user else None,
            created=self.created,
            updated=self.updated,
            last_used=self.last_used,
            last_rotated=self.last_rotated,
            retain_period_minutes=self.retain_period,
            active=self.active,
        )

    def update(self, update: APIKeyUpdateModel) -> "APIKeySchema":
        """Update an `APIKeySchema` with an `APIKeyUpdateModel`.

        Args:
            update: The update model.

        Returns:
            The updated `APIKeySchema`.
        """
        if update.name:
            self.name = update.name

        if update.description:
            self.description = update.description

        if update.active is not None:
            self.active = update.active

        self.updated = datetime.utcnow()
        return self

    def internal_update(
        self, update: APIKeyInternalUpdateModel
    ) -> "APIKeySchema":
        """Update an `APIKeySchema` with an `APIKeyInternalUpdateModel`.

        The internal update can also update the last used timestamp.

        Args:
            update: The update model.

        Returns:
            The updated `APIKeySchema`.
        """
        self.update(update)

        if update.update_last_used:
            self.last_used = self.updated

        return self

    def rotate(
        self,
        rotate_request: APIKeyRotateRequestModel,
    ) -> Tuple["APIKeySchema", str]:
        """Rotate the key for an `APIKeySchema`.

        Args:
            rotate_request: The rotate request model.

        Returns:
            The updated `APIKeySchema` and the new un-hashed key.
        """
        self.updated = datetime.utcnow()
        self.previous_key = self.key
        self.retain_period = rotate_request.retain_period_minutes
        new_key = self._generate_jwt_secret_key()
        self.key = self._get_hashed_key(new_key)
        self.last_rotated = self.updated

        return self, new_key
