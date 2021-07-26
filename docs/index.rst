.. Inference Server documentation master file, created by
   sphinx-quickstart on Wed Jun 16 03:02:58 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**Welcome to Inference Server's documentation!**
=================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Introduction
============================================
This project is *backend* of a bigger project **Autonomous Driving Simulation**. This backend deals with ML stuff that
are hard to do in unity.

System Design & Architecture
============================================
On the highest level unity sends raw sensor data to this server, and it provides analysis of that data back to unity.
   .. image:: _static/images/design.png


API Reference
-------------

If you are looking for information on a specific function, class or
method, this part of the documentation covers it.

.. toctree::
   :maxdepth: 2

   api