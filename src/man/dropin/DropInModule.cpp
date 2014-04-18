#include "DropInModule.h"

namespace man {
namespace dropin {

DropInModule::DropInModule()
:portals::test_(base())
{
}

DropInModule::~DropInModule()
{
}

void DropInModule::run_()
{
  portals::Message<messages::input> msg(0);
  i=msg.get();
  std::cout << "My x = " << i.get_my_x() << std::endl;
  i->set_my_x(3);
  std::cout << "My new x = " << i.get_my_x() << std::endl;

  test_.setMessage(i);
}

}
}
