# This time, the solution involves simply replacing scanf with our own version,
# since Angr does not support requesting multiple parameters with scanf.

import angr
import claripy
import sys

def main(argv):
  path_to_binary = argv[1]
  project = angr.Project(path_to_binary)

  initial_state = project.factory.entry_state()

  class ReplacementScanf(angr.SimProcedure):
    # Finish the parameters to the scanf function. Hint: 'scanf("%u %u", ...)'.
    # (!)
    def run(self, format_string, scanf0_address, scanf1_address):
      scanf0 = claripy.BVS('scanf0', 32)
      scanf1 = claripy.BVS('scanf1', 32)

      # The scanf function writes user input to the buffers to which the 
      # parameters point.
      self.state.memory.store(scanf0_address, scanf0, endness=project.arch.memory_endness)
      self.state.memory.store(scanf1_address, scanf1, endness=project.arch.memory_endness)

      # Now, we want to 'set aside' references to our symbolic values in the
      # globals plugin included by default with a state. You will need to
      # store multiple bitvectors. You can either use a list, tuple, or multiple
      # keys to reference the different bitvectors.
      # (!)
      self.state.globals['solution0'] = scanf0
      self.state.globals['solution1'] = scanf1

  scanf_symbol = 0x08048450
  project.hook(scanf_symbol, ReplacementScanf())

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Good Job' in stdout_output

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return b'Try again' in stdout_output

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    # Grab whatever you set aside in the globals dict.
    stored_solutions0 = solution_state.globals['solution0']
    stored_solutions0 = solution_state.solver.eval(stored_solutions0)
    stored_solutions1 = solution_state.globals['solution1']
    stored_solutions1 = solution_state.solver.eval(stored_solutions1)
    solution = "%u %u" % (stored_solutions0, stored_solutions1)

    print(solution)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
