"""
SENAContigo Central Model Registry.
Imports all SQLAlchemy models across all modules to ensure their classes and relationships are fully registered.
"""
import app.modules.identity.models  # noqa: F401
import app.modules.organization.models  # noqa: F401
import app.modules.academic.models  # noqa: F401
import app.modules.apprentices.models  # noqa: F401
import app.modules.contracts.models  # noqa: F401
import app.modules.variables.models  # noqa: F401
import app.modules.surveys.models  # noqa: F401
import app.modules.responses.models  # noqa: F401
import app.modules.needs.models  # noqa: F401
import app.modules.cases.models  # noqa: F401

import app.modules.followups.models  # noqa: F401
import app.modules.benefits.models  # noqa: F401
import app.modules.rules.models  # noqa: F401
import app.modules.segments.models  # noqa: F401
import app.modules.notifications.models  # noqa: F401
import app.modules.analytics.models  # noqa: F401
import app.modules.audit.models  # noqa: F401
