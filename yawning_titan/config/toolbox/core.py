from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import yaml

from yawning_titan.exceptions import (
    ConfigGroupValidationError,
    ConfigItemValidationError,
)

yaml.Dumper.ignore_aliases = lambda *args: True


class ConfigBase:
    """Used to provide helper methods to represent a ConfigGroup object."""

    def get_config_elements(
        self, _type: Optional[Union[ConfigItem, ConfigGroup]] = None
    ) -> Dict[str, Union[ConfigItem, ConfigGroup]]:
        """
        Get the attributes of the class that are either :class: `ConfigGroup` or :class:`ConfigItem`.

        :param _type: An optional type for a specific type of config element.

        :return: A dictionary of names to config elements.
        """
        if _type is not None:
            return {k: v for k, v in self.__dict__.items() if isinstance(v, _type)}
        return {
            k: v
            for k, v in self.__dict__.items()
            if isinstance(v, ConfigItem) or isinstance(v, ConfigGroup)
        }

    def get_non_config_elements(self) -> Dict[str, Any]:
        """
        Get all attributes of the class that are not :class: `ConfigGroup` or :class: `ConfigItem`.

        :return: A dictionary of names to attributes.
        """
        return {
            k: v
            for k, v in self.__dict__.items()
            if k not in self.get_config_elements()
        }

    def stringify(self):
        """Represent the class as a string.

        :return: A string.
        """
        string = f"{self.__class__.__name__}("
        strings = [
            f"{name}={val.stringify()}"
            for name, val in self.get_config_elements().items()
        ]
        strings.extend(
            [f"{name}={val}" for name, val in self.get_non_config_elements().items()]
        )
        return string + ", ".join(strings) + ")"

    def __repr__(self) -> str:
        """Return the result of :method: `ConfigBase.stringify`."""
        return self.stringify()

    def __str__(self) -> str:
        """Return the result of :method: `ConfigBase.stringify`."""
        return self.stringify()

    def __hash__(self) -> int:
        """Generate a unique hash for the class."""
        element_hash = [v.stringify() for v in self.get_config_elements().values()]
        element_hash.extend(
            [
                tuple(v) if isinstance(v, Iterable) else v
                for v in self.get_non_config_elements().values()
            ]
        )
        return hash(tuple(element_hash))

    def __eq__(self, other) -> bool:
        """Check the equality of any 2 instances of class.

        :param other: Another potential instance of the class to be compared against.

        :return: A boolean True if the elements holds the same data otherwise False.
        """
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return False


@dataclass()
class ItemTypeProperties(ABC):
    """An Abstract Base Class that is inherited by config data type properties."""

    allowed_types: List[type] = None
    """"""
    allow_null: Optional[bool] = None
    """`True` if the config _value can be left empty, otherwise `False`."""
    default: Optional[Any] = None
    """The items default value."""

    def __post_init__(self):
        if self.default:
            validated_default = self.validate(self.default)
            if not validated_default.passed:
                raise validated_default.fail_exceptions[0]

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        An abstract method that returns the properties as a dict.

        :return: A dict.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

    # @abstractmethod
    def validate(self, val) -> ConfigItemValidation:
        """Perform the base validation checks common to all `ConfigItem` elements.

        These checks include:
        - Check that the value is not null if :attribute: `allow_null` is False
        - Check that the type of the value is in :attribute: `allowed_types`
        """
        validation = ConfigItemValidation()
        try:
            if not self.allow_null and val is None:
                msg = f"Value {val} when allow_null is not permitted."
                raise ConfigItemValidationError(msg)
        except ConfigItemValidationError as e:
            validation.add_validation(msg, e)
        try:
            if not any(isinstance(val, _type) for _type in [int, float]):
                msg = (
                    f"Value {val} is of type {type(val)}, should be "
                    + " or ".join(map(str, self.allowed_types))
                    + "."
                )
                raise ConfigItemValidationError(msg)
        except ConfigItemValidationError as e:
            validation.add_validation(msg, e)
        return validation


@dataclass()
class ConfigItemValidation:
    """
    :class:`ConfigItemValidation` is used to return a validation result.

    If validation fails, a reason why and any exception raised are returned.
    """

    passed: Optional[bool] = True
    """``True`` if the _value has passed validation, otherwise ``False``."""
    fail_reason: Optional[str] = None
    """The reason why validation failed."""
    fail_exception: Optional[Exception] = None
    """The :class:`Exception` raised when validation failed."""

    def __post_init__(self):
        # print("CONFIG ITEM POST INIT")
        self.fail_reasons: List[str] = (
            [self.fail_reason] if self.fail_reason is not None else []
        )
        self.fail_exceptions: List[ConfigItemValidationError] = (
            [self.fail_exception] if self.fail_exception is not None else []
        )
        delattr(self, "fail_reason")
        delattr(self, "fail_exception")

    def add_validation(self, fail_reason: str, exception: ConfigItemValidationError):
        """
        Add a validation fail_reason, exception pair and set the validation result :attribute: passed as False.

        :param fail_reason: A string message to describe a particular error.
        :param exception: A wrapped `Exception` object that can be used to raise an error for the `fail_reason`.
        """
        self.passed = False
        print("$$", self.__class__.__name__, fail_reason, exception)
        self.fail_reasons.append(fail_reason)
        self.fail_exceptions.append(exception)


class ConfigGroupValidation(ConfigBase):
    """
    Used to return a validation result for a group of dependant config items, and the list of item validations.

    If validation fails, a reason why and any exception raised are returned.
    """

    def __init__(
        self,
        passed: bool = True,
        fail_reason: Optional[str] = None,
        fail_exception: Optional[ConfigGroupValidationError] = None,
    ):
        self.passed: bool = passed
        self.fail_reasons: List[str] = [fail_reason] if fail_reason is not None else []
        self.fail_exceptions: List[ConfigGroupValidationError] = (
            [fail_exception] if fail_exception is not None else []
        )
        self._element_validation = {}

    def add_element_validation(
        self,
        element_name: str,
        validation: Union[ConfigItemValidation, ConfigGroupValidation],
    ):
        """
        Add a :class:`ConfigItemValidation` or :class:`ConfigGroupValidation` to the item validation dict.

        :param element_name: The name of the element.
        :param validation: the instance of ConfigItemValidation.
        """
        self._element_validation[element_name] = validation

    def add_validation(self, fail_reason: str, exception: ConfigGroupValidationError):
        """
        Add a validation fail_reason, exception pair and set the validation result :attribute: passed as False.

        Additionally check that no such error already exists.

        :param fail_reason: A string message to describe a particular error.
        :param exception: A wrapped `Exception` object that can be used to raise an error for the `fail_reason`.
        """
        self.passed = False
        if fail_reason not in self.fail_reasons:
            self.fail_reasons.append(fail_reason)
        if exception not in self.fail_exceptions:
            self.fail_exceptions.append(exception)

    def to_dict(self, element_name: str = "root", root: bool = True) -> dict:
        """
        Express the error tree as a dictionary.

        :param element_name: A string name for the element to be represented.

        :return: A dict of element names to validation errors or validation dictionaries.
        """
        if self.passed:
            d = {}
        else:
            d = {"group": self.fail_reasons}
        for e, validation in self.element_validation.items():
            if isinstance(validation, ConfigGroupValidation) and (
                not validation.group_passed or not validation.passed
            ):
                d[e] = validation.to_dict(e, False)
            elif not validation.passed:
                d[e] = validation.fail_reasons

        if root:
            if not d:
                return {element_name: "Passed"}
            return {element_name: d}
        return d

    def log(self, element_name: str = "root") -> None:
        """
        Return the validation results as a formatted string.

        :param element_name: A string name for the element to be represented.
        """
        string = "\nValidation results\n" "------------------\n"
        d = self.to_dict(element_name)
        if d:
            string += yaml.dump(d, sort_keys=False, default_flow_style=False)
        else:
            string += d.get(element_name, "Passed")
        print(string)

    @property
    def element_validation(self) -> Dict[str, ConfigItemValidation]:
        """
        The dict of element to :class:`ConfigItemValidation` and :class:`ConfigGroupValidation` validations.

        :return: A dict.
        """
        return self._element_validation

    @property
    def group_passed(self) -> bool:
        """
        Returns True if all items passed validation, otherwise returns False.

        :return: A bool.
        """
        return all(v.passed for v in self.element_validation.values())


@dataclass
class ConfigItem:
    """The ConfigItem class holds an items value, doc, and properties."""

    value: object
    """The items value."""
    doc: Optional[str] = None
    """The items doc."""
    properties: Optional[ItemTypeProperties] = None
    """The items properties."""
    validation: ConfigItemValidation = None
    """The instance of ConfigItemValidation that provides access to the item validation details."""

    def __post_init__(self):
        if self.value is None and self.properties.default:
            self.value = self.properties.default
        self.validation = self.properties.validate(self.value)

    def to_dict(self, as_key_val_pair: bool = False):
        """
        Return the ConfigItem as a dict.

        :param as_key_val_pair: If true, the dict is returned as a value in
            a key/value pair, the key being the class name.
        :return: The ConfigItem as a dict.
        """
        d = {"value": self.value}
        if self.doc:
            d["doc"] = self.doc
        if self.properties:
            d["properties"] = self.properties.to_dict()
        if as_key_val_pair:
            return {self.__class__.__name__: d}
        return d

    def validate(self) -> ConfigItemValidation:
        """
        Validate the item against its properties.

        If no properties exist,
        simply return a default passed :class:`ConfigItemValidation`.

        :return: An instance of :class:`ConfigItemValidation`.
        """
        # print("VALIDATING ITEM")
        if self.properties:
            return self.properties.validate(self.value)
        return ConfigItemValidation()

    def set_value(self, value: Any) -> None:
        """
        Set the value of the :class:`ConfigItem` bypassing the validation.

        :param value: The value to be set.
        """
        self.__dict__["value"] = value

    def __setattr__(self, __name: str, __value: Any) -> None:
        """
        Set an attribute of the `ConfigItem` if the value is to be set, call the validation method.

        :param __name: the name of the attribute to be set
        :param __value: the value to set the attribute to
        """
        self.__dict__[__name] = __value
        if __name == "value":
            self.validate()

    def stringify(self):
        """This is here to allow stringify methods to be call on both :class: `ConfigItem` and :class: `ConfigGroup` classes."""
        return self.value


class ConfigGroup(ConfigBase, ABC):
    """The ConfigGroup class holds a ConfigItem's, doc, properties, and a ConfigItemValidation."""

    def __init__(self, doc: Optional[str] = None):
        """The ConfigGroup constructor.

        :param doc: The groups doc.
        """
        self.doc: Optional[str] = doc
        self.validation = self.validate()

    def validate(self) -> ConfigGroupValidation:
        """
        Validate the grouped items against their properties.

        :return: An instance of :class:`ConfigGroupValidation`.
        """
        print("VALIDATE IN BASE CONFIG GROUP", self.__class__.__name__)
        if not hasattr(self, "validation"):
            print("SETTING VALIDATION ATTR", self.__class__.__name__)
            self.validation = ConfigGroupValidation()
        self.validate_elements()
        return self.validation

    def to_dict(self):
        """
        Return the ConfigGroup as a dict.

        :return: The ConfigGroup as a dict.
        """
        attr_dict = {"doc": self.doc} if self.doc is not None else {}
        element_dict = {k: e.to_dict() for k, e in self.get_config_elements().items()}
        return {**attr_dict, **element_dict}

    def validate_elements(self):
        """Call the .validate() method on each of the elements in the group."""
        for k, element in self.get_config_elements().items():
            self.validation.add_element_validation(k, element.validate())

    def set_from_dict(self, config_dict: dict, root: bool = True):
        """
        Set the values of all :class: `ConfigGroup` or :class:`ConfigItem` elements.

        :param config_dict: A dictionary representing values of all config elements.
        :param root: Whether the element is a base level element or not.
            if the element is a root then it should validate all of its descendants.
        """
        # print("-----------------\nSETTING FROM DICT\n-----------------")
        for element_name, v in config_dict.items():
            element = getattr(self, element_name, None)
            if type(v) == dict and isinstance(element, ConfigGroup):
                element.set_from_dict(v, False)
            elif type(v) != dict and isinstance(element, ConfigItem):
                element.set_value(v)
        if root:
            self.validate()
