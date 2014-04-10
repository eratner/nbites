#pragma once

#include "RoboGrams.h"

namespace man {
namespace dropin {

class DropInModule : public portals::Module
{
public:
  DropInModule();

  virtual ~DropInModule();

private:
  void run_();

};

}
}
