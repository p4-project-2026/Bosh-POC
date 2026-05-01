class Flags:
	logv = False
	logvv = False
	logvvv = False

	def set_flag(self, flag: str) -> None:
		if flag == "-v":
			Flags.logv = True
		elif flag == "-vv":
			Flags.logv = True
			Flags.logvv = True
		elif flag == "-vvv":
			Flags.logv = True
			Flags.logvv = True
			Flags.logvvv = True
		else:
			print(f"Warning: Unrecognized flag '{flag}'")