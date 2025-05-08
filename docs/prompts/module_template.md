# Module Template

## Overview
This template provides guidance for creating new modules in the AI Artist Creation and Management System. Use this structure to ensure consistency across the codebase.

## Module Structure

```
module_name/
├── __init__.py           # Exports public interfaces
├── core.py               # Core functionality
├── models.py             # Data models and schemas
├── utils.py              # Helper functions
├── exceptions.py         # Module-specific exceptions
├── config.py             # Configuration handling
└── test_*.py             # Unit tests
```

## Implementation Guidelines

### Step 1: Define the Interface
Begin by defining the public interface for your module. What functionality will it expose to other modules?

```python
# __init__.py
from .core import ModuleNameManager
from .models import ModuleNameConfig, ModuleNameResult
from .exceptions import ModuleNameError

__all__ = ['ModuleNameManager', 'ModuleNameConfig', 'ModuleNameResult', 'ModuleNameError']
```

### Step 2: Create Data Models
Define the data models that your module will use, preferably using Pydantic.

```python
# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ModuleNameConfig(BaseModel):
    """Configuration for the ModuleName module."""
    parameter_1: str = Field(..., description="Description of parameter 1")
    parameter_2: int = Field(42, description="Description of parameter 2")
    optional_param: Optional[str] = Field(None, description="Optional parameter")
    
    class Config:
        extra = "forbid"  # Prevent extra fields

class ModuleNameResult(BaseModel):
    """Result from ModuleName operations."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(..., description="Result data")
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### Step 3: Implement Core Functionality
Implement the core functionality of your module.

```python
# core.py
import logging
from typing import Dict, Any, Optional
from .models import ModuleNameConfig, ModuleNameResult
from .exceptions import ModuleNameError

logger = logging.getLogger(__name__)

class ModuleNameManager:
    """Manager class for ModuleName functionality."""
    
    def __init__(self, config: ModuleNameConfig):
        """Initialize with configuration."""
        self.config = config
        logger.info(f"ModuleNameManager initialized with config: {config}")
    
    def process(self, input_data: Dict[str, Any]) -> ModuleNameResult:
        """Process input data and return a result."""
        try:
            logger.debug(f"Processing input: {input_data}")
            
            # Implementation logic here
            result_id = "generated_id"  # Generate appropriate ID
            result_data = {"processed": True, "input": input_data}
            
            result = ModuleNameResult(
                id=result_id,
                data=result_data
            )
            
            logger.info(f"Successfully processed input, result ID: {result_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}", exc_info=True)
            raise ModuleNameError(f"Failed to process input: {str(e)}") from e
```

### Step 4: Define Exceptions
Create custom exceptions for your module.

```python
# exceptions.py
class ModuleNameError(Exception):
    """Base exception for ModuleName module."""
    pass

class ModuleNameConfigError(ModuleNameError):
    """Exception raised for configuration errors."""
    pass

class ModuleNameProcessingError(ModuleNameError):
    """Exception raised for processing errors."""
    pass
```

### Step 5: Implement Helper Functions
Create utility functions to support your module.

```python
# utils.py
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def validate_input(input_data: Dict[str, Any]) -> bool:
    """Validate input data for processing."""
    # Validation logic here
    return True

def transform_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform data for processing."""
    # Transformation logic here
    return data
```

### Step 6: Write Tests
Create comprehensive tests for your module.

```python
# test_core.py
import unittest
from .core import ModuleNameManager
from .models import ModuleNameConfig
from .exceptions import ModuleNameError

class TestModuleNameManager(unittest.TestCase):
    
    def setUp(self):
        self.config = ModuleNameConfig(parameter_1="test")
        self.manager = ModuleNameManager(self.config)
    
    def test_process_valid_input(self):
        input_data = {"key": "value"}
        result = self.manager.process(input_data)
        self.assertEqual(result.data["input"], input_data)
        self.assertTrue(result.data["processed"])
    
    def test_process_invalid_input(self):
        with self.assertRaises(ModuleNameError):
            self.manager.process(None)
```

## Integration Guidelines

### Dependency Injection
- Use dependency injection to provide required services to your module
- Avoid direct imports of concrete implementations from other modules
- Use interfaces (abstract base classes) to define dependencies

### Error Handling
- Catch specific exceptions, not generic ones
- Always include context in error messages
- Log errors with appropriate severity levels
- Propagate errors as module-specific exceptions

### Logging
- Use the standard logging module
- Include appropriate context in log messages
- Use debug level for detailed information
- Use info level for normal operations
- Use warning level for concerning but non-error situations
- Use error level for exceptions and failures

### Configuration
- Use environment variables for configuration when possible
- Provide sensible defaults for all configuration options
- Validate configuration at startup
- Document all configuration options

## Documentation Requirements

- Include docstrings for all public classes and methods
- Document parameters, return values, and exceptions
- Provide usage examples in docstrings
- Update module documentation when making changes
- Add entries to the development diary for significant changes
