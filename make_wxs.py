"""Builds installer.wxs (WiX v4/v5) from the PyInstaller output folder.

Usage: python make_wxs.py <dist_folder> <exe_file_name> <version>
"""
import os
import sys
from xml.sax.saxutils import quoteattr

dist_dir = sys.argv[1]
exe_name = sys.argv[2]
version = sys.argv[3] if len(sys.argv) > 3 else "1.0.0"

PRODUCT = "KavasuDynoPOSB Calcy"
MANUFACTURER = "KAVASU"
UPGRADE_CODE = "5DB87680-2A34-4597-9000-60F6F672B3E0"
REG_KEY = "SOFTWARE\\KAVASU\\" + PRODUCT


def q(s):
    return quoteattr(s)


dir_ids = {"": "INSTALLFOLDER"}
comp_lines = []
n = 0


def dir_id(rel):
    """Create (once) a Directory id for a relative folder path."""
    if rel in dir_ids:
        return dir_ids[rel]
    parent, name = os.path.split(rel)
    dir_id(parent)
    dir_ids[rel] = "d%d" % len(dir_ids)
    return dir_ids[rel]


for root, dirs, files in os.walk(dist_dir):
    dirs.sort()
    rel = os.path.relpath(root, dist_dir)
    rel = "" if rel == "." else rel
    for name in sorted(files):
        if rel == "" and name == exe_name:
            continue  # the main exe is authored separately
        n += 1
        did = dir_id(rel)
        src = os.path.join(dist_dir, rel, name) if rel else os.path.join(dist_dir, name)
        comp_lines.append(
            '      <Component Id="c%d" Directory="%s"><File Id="f%d" Source=%s KeyPath="yes" /></Component>'
            % (n, did, n, q(src)))


def render_dirs(parent_rel, indent):
    out = []
    kids = sorted(r for r in dir_ids if r and os.path.dirname(r) == parent_rel)
    for r in kids:
        name = os.path.basename(r)
        sub = render_dirs(r, indent + "  ")
        if sub:
            out.append('%s<Directory Id="%s" Name=%s>' % (indent, dir_ids[r], q(name)))
            out.extend(sub)
            out.append('%s</Directory>' % indent)
        else:
            out.append('%s<Directory Id="%s" Name=%s />' % (indent, dir_ids[r], q(name)))
    return out


exe_src = os.path.join(dist_dir, exe_name)

x = []
x.append('<?xml version="1.0" encoding="UTF-8"?>')
x.append('<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs">')
x.append('  <Package Name=%s Manufacturer=%s Version=%s UpgradeCode="%s" Scope="perMachine" Language="1033">'
         % (q(PRODUCT), q(MANUFACTURER), q(version), UPGRADE_CODE))
x.append('    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />')
x.append('    <MediaTemplate EmbedCab="yes" />')
x.append('    <Icon Id="AppIcon.ico" SourceFile="assets\\icon.ico" />')
x.append('    <Property Id="ARPPRODUCTICON" Value="AppIcon.ico" />')
x.append('')
x.append('    <!-- Default install folder: Program Files\\KAVASU -->')
x.append('    <StandardDirectory Id="ProgramFilesFolder">')
x.append('      <Directory Id="INSTALLFOLDER" Name="KAVASU" />')
x.append('    </StandardDirectory>')
x.append('')
x.append('    <!-- Does the KAVASU folder already exist? -->')
x.append('    <Property Id="KAVASU_FOUND" Secure="yes">')
x.append('      <DirectorySearch Id="KavasuDirSearch" Path="[ProgramFilesFolder]KAVASU" />')
x.append('    </Property>')
x.append('    <!-- Is this product already installed (upgrade / repair / uninstall)? -->')
x.append('    <Property Id="PRIORINSTALLDIR" Secure="yes">')
x.append('      <RegistrySearch Id="PriorDirSearch" Root="HKLM" Key=%s Name="InstallDir" Type="directory" />' % q(REG_KEY))
x.append('    </Property>')
x.append('')
x.append('    <CustomAction Id="SetPriorDir" Directory="INSTALLFOLDER" Value="[PRIORINSTALLDIR]" />')
x.append('    <CustomAction Id="SetSubDir" Directory="INSTALLFOLDER" Value=%s />'
         % q("[ProgramFilesFolder]KAVASU\\" + PRODUCT + "\\"))
x.append('    <InstallUISequence>')
x.append('      <Custom Action="SetPriorDir" After="AppSearch" Condition="PRIORINSTALLDIR" />')
x.append('      <Custom Action="SetSubDir" After="SetPriorDir" Condition="KAVASU_FOUND AND NOT PRIORINSTALLDIR" />')
x.append('    </InstallUISequence>')
x.append('    <InstallExecuteSequence>')
x.append('      <Custom Action="SetPriorDir" After="AppSearch" Condition="PRIORINSTALLDIR" />')
x.append('      <Custom Action="SetSubDir" After="SetPriorDir" Condition="KAVASU_FOUND AND NOT PRIORINSTALLDIR" />')
x.append('    </InstallExecuteSequence>')
x.append('')
x.append('    <Feature Id="Main" Title=%s Level="1">' % q(PRODUCT))
x.append('      <ComponentGroupRef Id="MainExeGroup" />')
x.append('      <ComponentGroupRef Id="AppFiles" />')
x.append('    </Feature>')
x.append('  </Package>')
x.append('')
x.append('  <Fragment>')
x.append('    <ComponentGroup Id="MainExeGroup">')
x.append('      <Component Id="MainExe" Directory="INSTALLFOLDER">')
x.append('        <File Id="MainExeFile" Source=%s KeyPath="yes">' % q(exe_src))
x.append('          <Shortcut Id="DesktopShortcut" Directory="DesktopFolder" Name=%s WorkingDirectory="INSTALLFOLDER" Icon="AppIcon.ico" />' % q(PRODUCT))
x.append('          <Shortcut Id="StartMenuShortcut" Directory="ProgramMenuFolder" Name=%s WorkingDirectory="INSTALLFOLDER" Icon="AppIcon.ico" />' % q(PRODUCT))
x.append('        </File>')
x.append('        <RegistryValue Root="HKLM" Key=%s Name="InstallDir" Type="string" Value="[INSTALLFOLDER]" />' % q(REG_KEY))
x.append('      </Component>')
x.append('    </ComponentGroup>')
x.append('  </Fragment>')
x.append('')
x.append('  <Fragment>')
x.append('    <DirectoryRef Id="INSTALLFOLDER">')
x.extend(render_dirs("", "      "))
x.append('    </DirectoryRef>')
x.append('  </Fragment>')
x.append('')
x.append('  <Fragment>')
x.append('    <ComponentGroup Id="AppFiles">')
x.extend(comp_lines)
x.append('    </ComponentGroup>')
x.append('  </Fragment>')
x.append('</Wix>')

with open("installer.wxs", "w", encoding="utf-8") as f:
    f.write("\n".join(x) + "\n")
print("installer.wxs written: %d files, %d folders, version %s" % (n, len(dir_ids) - 1, version))
