#Author-Dmytro Kyrychuk
#Description-Assign random appearance to each body.

# Copyright (C) 2015 Dmytro Kyrychuk
#
# This source file is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


"""
Icons made by Freepik from www.flaticon.com
"""

import traceback
import os
from random import randrange

import adsk.core
import adsk.fusion

commandId = 'AssignRandomAppearancesId'
MODIFY_PANEL_ID = 'SolidModifyPanel'
FUSION_PRODUCT_TYPE = 'DesignProductType'

BUTTON_PLACE_NEAR_ID = 'AppearanceCommand'
BUTTON_PLACE_BEFORE = False

# global set of event handlers to keep them referenced for the duration of
# the command
handlers = []


def commandDefinitionById(id):
    app = adsk.core.Application.get()
    ui = app.userInterface
    if not id:
        ui.messageBox('commandDefinition id is not specified')
        return None
    commandDefinitions_ = ui.commandDefinitions
    commandDefinition_ = commandDefinitions_.itemById(id)
    return commandDefinition_


def commandControlById(id):
    app = adsk.core.Application.get()
    ui = app.userInterface
    if not id:
        ui.messageBox('commandControl id is not specified')
        return None
    workspaces_ = ui.workspaces
    modelingWorkspace_ = workspaces_.itemById('FusionSolidEnvironment')
    toolbarPanels_ = modelingWorkspace_.toolbarPanels
    toolbarPanel_ = toolbarPanels_.itemById(MODIFY_PANEL_ID)
    toolbarControls_ = toolbarPanel_.controls
    toolbarControl_ = toolbarControls_.itemById(id)
    return toolbarControl_


def destroyObject(uiObj, tobeDeleteObj):
    if uiObj and tobeDeleteObj:
        if tobeDeleteObj.isValid:
            tobeDeleteObj.deleteMe()
        else:
            uiObj.messageBox('tobeDeleteObj is not a valid object')


def iter_adsk(container):
    for index in range(container.count):
        yield container.item(index)


def get_random_material_library(app):
    """
    :type app: adsk.core.Application
    :rtype: adsk.core.MaterialLibrary
    """
    libs = app.materialLibraries
    return libs.item(randrange(libs.count))


def get_random_appearance(app):
    """
    :type app: adsk.core.Application
    :rtype: adsk.core.Appearance
    """
    material_library = get_random_material_library(app)
    appearances = material_library.appearances
    return appearances.item(randrange(appearances.count))


def assign_random_appearance_to_active_document_bodies(app):
    """Assigns random appearance to active document's bodies.

    :type app: adsk.core.Application
    """
    for product in iter_adsk(app.activeDocument.products):
        if str(product.productType) == str(FUSION_PRODUCT_TYPE):
            for component in iter_adsk(product.allComponents):
                for bRepBody in iter_adsk(component.bRepBodies):
                    bRepBody.appearance = get_random_appearance(app)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        if app:
            ui = app.userInterface

        class AssignRandomAppearanceCommandExecuteHandler(
                adsk.core.CommandEventHandler):
            def __init__(self):
                super().__init__()

            def notify(self, args):
                try:
                    assign_random_appearance_to_active_document_bodies(app)

                except:
                    if ui:
                        ui.messageBox(
                            'Failed:\n{}'.format(traceback.format_exc()))

        class AssignRandomAppearanceCommandCreatedHandler(
                adsk.core.CommandCreatedEventHandler):
            def __init__(self):
                super().__init__()

            def notify(self, args):
                try:
                    cmd = args.command
                    onExecute = AssignRandomAppearanceCommandExecuteHandler()
                    cmd.execute.add(onExecute)
                    # keep the handler referenced beyond this function
                    handlers.append(onExecute)

                except:
                    if ui:
                        ui.messageBox(
                            'Failed:\n{}'.format(traceback.format_exc()))

        # add a command on create panel in modeling workspace
        commandName = 'Assign Random Appearances'
        commandDescription = 'Assign Random Appearances to each design ' \
                             'component.'
        workspaces_ = ui.workspaces
        modelingWorkspace_ = workspaces_.itemById('FusionSolidEnvironment')
        toolbarPanels_ = modelingWorkspace_.toolbarPanels
        toolbarPanel_ = toolbarPanels_.itemById(MODIFY_PANEL_ID)
        toolbarControls_ = toolbarPanel_.controls
        toolbarControl_ = toolbarControls_.itemById(commandId)
        if toolbarControl_:
            ui.messageBox('Appearance assigning command is already loaded.')
            adsk.terminate()
            return
        else:
            commandDefinition_ = ui.commandDefinitions.itemById(commandId)
            if not commandDefinition_:
                resourceDir = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), 'resources')
                commandDefinition_ = ui.commandDefinitions.addButtonDefinition(
                    commandId, commandName, commandDescription, resourceDir)
            onCommandCreated = AssignRandomAppearanceCommandCreatedHandler()
            commandDefinition_.commandCreated.add(onCommandCreated)
            # keep the handler referenced beyond this function
            handlers.append(onCommandCreated)
            toolbarControl_ = toolbarControls_.addCommand(
                commandDefinition_, BUTTON_PLACE_NEAR_ID, BUTTON_PLACE_BEFORE)
            toolbarControl_.isVisible = True

            if not context['IsApplicationStartup']:
                ui.messageBox(
                    'Add-in is loaded successfully.\r\n\r\n'
                    'A command is added to the Modify panel in modeling'
                    ' workspace.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            adsk.terminate()


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        objArray = []

        commandControl_ = commandControlById(commandId)
        if commandControl_:
            objArray.append(commandControl_)

        commandDefinition_ = commandDefinitionById(commandId)
        if commandDefinition_:
            objArray.append(commandDefinition_)

        for obj in objArray:
            destroyObject(ui, obj)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
