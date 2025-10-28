@echo off
mkdir schema\archive 2>nul
move schema\characters_v2.sql schema\archive\
move schema\character_modifiers.sql schema\archive\
move schema\gear_system.sql schema\archive\
move schema\query_logs.sql schema\archive\
echo Schema files archived successfully!
