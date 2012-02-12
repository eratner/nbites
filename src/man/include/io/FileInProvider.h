/**
 * @class FileInProvider
 *
 * Opens a file descriptor for reading from the specified file.
 *
 */

#pragma once

#include <iostream>
#include <fcntl.h>
#include <string>
#include <cerrno>
#include "InProvider.h"
#include "FileDefs.h"

namespace common {
namespace io {

class FileInProvider : public InProvider {

public:
    FileInProvider(std::string file_name) :
                file_name(file_name),
                is_open(false) {
    }

    virtual ~FileInProvider() {
        fclose(file);
    }

    virtual std::string debugInfo() const {
        return "file name: " + file_name;
    }

    virtual bool isOfTypeStreaming() const { return false; }

    virtual bool reachedEnd() const {
        return feof(file);
    }

    virtual long int getCurrentPosition() const {
        uint32_t result;
        return ftell(file);
        return result;
    }

    virtual bool rewind(long int offset) const {
        if (offset <= getCurrentPosition()) {
            int result = fseek(file, -offset, SEEK_CUR);
            if (result == 0) {
                return true;
            }
        }
        return false;
    }

    virtual uint32_t readCharBuffer(char* buffer, uint32_t size) const throw (file_read_exception) {
        if (!opened()) {
            throw file_read_exception(file_read_exception::NOT_OPEN);
        }

        uint32_t result = 0;
        result = fread(buffer, sizeof(char), size, file);

        if (ferror(file)) {
            throw file_read_exception(file_read_exception::READ, ferror(file));
        }

        return result;
    }

    virtual void peekAt(char* buffer, uint32_t size) const throw (file_read_exception) {
        this->readCharBuffer(buffer, size);
        this->rewind(size);
    }

    void openCommunicationChannel() throw (file_exception) {

        file = fopen(file_name.c_str(), "rb");

        if (file == NULL) {
            throw file_exception(file_exception::CREATE_ERR, errno);
        }

        is_open= true;
    }

    virtual bool opened() const {
        return is_open;
    }

private:
    std::string file_name;
    bool is_open;
    FILE* file;

};

}
}
