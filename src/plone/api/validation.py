# -*- coding: utf-8 -*-
"""Decorators for validating parameters"""

import inspect
from decorator import decorator
from plone.api.exc import InvalidParameterError
from plone.api.exc import MissingParameterError


def _get_arg_spec(func, validator_args):
    """Get the arguments specified in the function spec
    and check that the decorator doesn't refer to non-existant args
    """
    signature_args, _, _, _ = inspect.getargspec(func)

    extra_args = set(validator_args) - set(signature_args)
    if extra_args:
        raise ValueError(
            "Validator for {0} refers to parameters "
            "that are not part of the function signature: {1}".format(
                func.__name__, ", ".join(extra_args))
        )

    return signature_args


def _get_supplied_args(signature_params, args, kwargs):
    """Return names of all args that have been passed in
    either as positional or keyword arguments, and are not None
    """
    supplied_args = {}
    for i in range(len(args)):
        if args[i] is not None:
            supplied_args[signature_params[i]] = args[i]

    for k, v in kwargs.iteritems():
        if v is not None:
            supplied_args[k] = v

    return supplied_args


def required_parameters(*required_params):
    """A decorator that tests whether all of the specified parameters
    have been supplied and are not None

    Todo: add an optional flag to allow None values through as valid parameters

    Usage:
    @required_parameters('a', 'b')
    def foo(a=None, b=None, c=None):
        pass
    """
    def _required_parameters(func):
        """The actual decorator"""
        signature_params = _get_arg_spec(func, required_params)

        def wrapped(f, *args, **kwargs):
            """The wrapped function (whose docstring will get replaced)"""
            supplied_args = _get_supplied_args(signature_params, args, kwargs)

            missing = [p for p in required_params if p not in supplied_args]
            if len(missing):
                raise MissingParameterError(
                    "Missing required parameter(s): {0}".format(
                        ", ".join(missing))
                )

            return f(*args, **kwargs)

        return decorator(wrapped, func)

    return _required_parameters


def mutually_exclusive_parameters(*exclusive_params):
    """A decorator that raises an exception if more than one
    of the specified parameters has been supplied and is not None

    Usage:
    @mutually_exclusive_parameters('a', 'b')
    def foo(a=None, b=None, c=None):
        pass
    """
    def _mutually_exclusive_parameters(func):
        """The actual decorator."""
        signature_params = _get_arg_spec(func, exclusive_params)

        def wrapped(f, *args, **kwargs):
            """The wrapped function (whose docstring will get replaced)."""
            supplied_args = _get_supplied_args(signature_params, args, kwargs)
            clashes = [s for s in supplied_args if s in exclusive_params]
            if len(clashes) > 1:
                raise InvalidParameterError(
                    "These parameters are mutually exclusive: {0}.".format(
                        ", ".join(supplied_args))
                )

            return f(*args, **kwargs)

        return decorator(wrapped, func)

    return _mutually_exclusive_parameters


def required_parameter_type(parameter_name="", parameter_type=None):
    """A decorator that raises an exception if a particular parameter
    is not of the required type

    Usage:
    @parameter_of_type(parameter='id', parameter_type=str):
    def create(id=None):
        pass
    """
    def _parameter_of_type(func):
        """The actual decorator"""
        signature_params = _get_arg_spec(func, ())

        def wrapped(f, *args, **kwargs):
            """The wrapped function (whose docstring will get replaced)"""

            supplied_args = _get_supplied_args(signature_params, args, kwargs)
            param_value = supplied_args.get(parameter_name, None)

            if param_value and not isinstance(param_value, parameter_type):
                raise InvalidParameterError(
                    "The '{0}' parameter is of type {1} but should be of "
                    "type {2}.".format(
                        parameter_name, type(param_value), parameter_type)
                )

            return f(*args, **kwargs)

        return decorator(wrapped, func)

    return _parameter_of_type


def at_least_one_of(*candidate_params):
    """A decorator that raises an exception if none of the
    specified parameters has been supplied.  Can be used in conjunction with
    mutually_exclusive_parameters to enforce exactly one.

    Usage:
    @at_least_one_of('a', 'b')
    def foo(a=None, b=None, c=None):
        pass
    """
    def _at_least_one_of(func):
        """The actual decorator."""
        signature_params = _get_arg_spec(func, candidate_params)

        def wrapped(f, *args, **kwargs):
            """The wrapped function (whose docstring will get replaced)."""
            supplied_args = _get_supplied_args(signature_params, args, kwargs)
            candidates = [s for s in supplied_args if s in candidate_params]
            if len(candidates) < 1:
                raise MissingParameterError(
                    "At least one of these parameters must be "
                    "supplied: {0}.".format(", ".join(candidate_params))
                )

            return f(*args, **kwargs)

        return decorator(wrapped, func)

    return _at_least_one_of
