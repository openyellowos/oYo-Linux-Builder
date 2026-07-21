
/* DING: Desktop Icons New Generation for GNOME Shell
 *
 * Copyright (C) 2021 Sundeep Mediratta (smedius@gmail.com)
 * Copyright (C) 2019 Sergio Costas (rastersoft@gmail.com)
 * Based on code original (C) Carlos Soriano
 * SwitcherooControl code based on code original from Marsch84
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
'use strict';
const Gdk = imports.gi.Gdk;
const desktopIconItem = imports.desktopIconItem;

const Prefs = imports.preferences;

const Signals = imports.signals;
const Gettext = imports.gettext.domain('ding');

const _ = Gettext.gettext;


var stackItem = class extends desktopIconItem.desktopIconItem {
    constructor(desktopManager, file, attributeContentType, fileExtra) {
        super(desktopManager, fileExtra);
        this._isSpecial = false;
        this._file = file;
        this.isStackTop = true;
        this.stackUnique = false;
        this._size = null;
        this._modifiedTime = null;
        this._attributeContentType = attributeContentType;
        this._createIconActor();
        this._createStackTopIcon();
        this._setLabelName(this._file);
        this.setAccessibleName(this._getVisibleName());
    }

    _createStackTopIcon() {
        const scale = this._icon.get_scale_factor();
        let pixbuf;
        let folder = 'folder';
        if (Prefs.getUnstackList().includes(this._attributeContentType)) {
            folder = 'folder-open';
        }
        pixbuf = this._createEmblemedIcon(null, `${folder}`);
        let surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, scale, null);
        this._icon.set_from_surface(surface);
    }

    doOpen() {
        this._desktopManager.onToggleStackUnstackThisTypeClicked(this.attributeContentType);
    }
    _doButtonOnePressed(event, shiftPressed, controlPressed) {
        this._desktopManager.onToggleStackUnstackThisTypeClicked(this.attributeContentType);
    }

    setSelected() {
    }

    updateIcon() {
        this._createStackTopIcon();
    }

    _getVisibleName() {
        return this._currentFileName;
    }

    setAccessibleName(filename) {
        /** TRANSLATORS: when using a screen reader, this is the role used when a stack is
         * unexpanded, or contracted. Example: if a stack named "pictures" is contracted, it will say "pictures Stack Unexpanded".
         * It is mandatory to say the file name first and the role after. */
        const unexpanded = _('${VisibleName} Stack Unexpanded');
        /** TRANSLATORS: when using a screen reader, this is the role used when a stack is
         * expanded. Example: if a stack named "pictures" is expanded (thus, their content is visible), it will say "pictures Stack Expanded".
         * It is mandatory to say the file name first and the role after. */
        const expanded = _('${VisibleName} Stack Expanded');
        const isExpanded = Prefs.getUnstackList().includes(this.attributeContentType);

        const accessible = this._containerAccessibility.get_accessible();
        const visibleNameAndRole = (isExpanded ? expanded : unexpanded).replace('${VisibleName}', filename);
        accessible.set_name(visibleNameAndRole);
    }

    /** *********************
     * Getters and setters *
     ***********************/

    get attributeContentType() {
        return this._attributeContentType;
    }

    get displayName() {
        return this._file;
    }

    get file() {
        return this._file;
    }

    get fileName() {
        return this._file;
    }

    get fileSize() {
        return this._size;
    }

    get isAllSelectable() {
        return false;
    }

    get modifiedTime() {
        return this._modifiedTime;
    }

    get path() {
        return `/tmp/${this._file}`;
    }

    get uri() {
        return `file:///tmp/${this._file}`;
    }

    get isStackMarker() {
        return true;
    }

    set size(size) {
        this._size = size;
    }

    set time(time) {
        this._modifiedTime = time;
    }
};
Signals.addSignalMethods(stackItem.prototype);
