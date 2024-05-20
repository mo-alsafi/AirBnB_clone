#!/usr/bin/python
"""
Console interpreter
"""
import cmd
import re
import shlex
import ast
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models.state import State
from models.city import City


def curly_braces_spliter(ea_arg):
    """
    Spliter for update
    """
    curly_braces = re.search(r"\{(.*?)\}", ea_arg)

    if curly_braces:
        id_with_comma = shlex.split(ea_arg[:curly_braces.span()[0]])
        id = [i.strip(",") for i in id_with_comma][0]

        str_data = curly_braces.group(1)
        try:
            arg_dict = ast.literal_eval("{" + str_data + "}")
        except Exception:
            print("**  invalid dictionary format **")
            return
        return id, arg_dict
    else:
        cmds = ea_arg.split(",")
        if cmds:
            try:
                id = cmds[0]
            except Exception:
                return "", ""
            try:
                attr_name = cmds[1]
            except Exception:
                return id, ""
            try:
                attr_value = cmds[2]
            except Exception:
                return id, attr_name
            return f"{id}", f"{attr_name} {attr_value}"


class HBNBCommand(cmd.Cmd):
    """
    HBNBCommand console class
    """
    prompt = "(hbnb) "
    valid_classes = ["BaseModel", "User", "Amenity",
                     "Place", "Review", "State", "City"]

    def emptyline(self):
        """
        Do nothing when an empty line is entered.
        """
        pass

    def default(self, arg):
        """
        Default behavior for cmd module when input is invalid
        """
        arg_list = arg.split('.')

        cls_nm = arg_list[0]  # incoming class name

        command = arg_list[1].split('(')

        cmd_met = command[0]  # incoming command method

        ea_arg = command[1].split(')')[0]  # extra arguments

        method_dict = {
                'all': self.do_all,
                'show': self.do_show,
                'destroy': self.do_destroy,
                'update': self.do_update,
                'count': self.do_count
                }

        if cmd_met in method_dict.keys():
            if cmd_met != "update":
                return method_dict[cmd_met]("{} {}".format(cls_nm, ea_arg))
            else:
                if not cls_nm:
                    print("** class name missing **")
                    return
                try:
                    obj_id, arg_dict = curly_braces_spliter(ea_arg)
                except Exception:
                    pass
                try:
                    call = method_dict[cmd_met]
                    return call("{} {} {}".format(cls_nm, obj_id, arg_dict))
                except Exception:
                    pass
        else:
            print("*** Unknown syntax: {}".format(arg))
            return False

    def do_EOF(self, arg):
        """
        exit program
        """
        return True

    def do_quit(self, arg):
        """
        Qeuit the program.
        """
        return True

    def do_create(self, arg):
        """
        Create a new instance of BaseModel and save it to the JSON file.
        Usage: create <class_name>
        """
        cmds = shlex.split(arg)

        if len(cmds) == 0:
            print("** class name missing **")
        elif cmds[0] not in self.valid_classes:
            print("** class doesn't exist **")
        else:
            new_instance = eval(f"{cmds[0]}()")
            storage.save()
            print(new_instance.id)

    def do_show(self, arg):
        """
        To show string representation of an instance.
        Usage: show <class_name> <id>
        """
        cmds = shlex.split(arg)

        if len(cmds) == 0:
            print("** class name missing **")
        elif cmds[0] not in self.valid_classes:
            print("** class doesn't exist **")
        elif len(cmds) < 2:
            print("** instance id missing **")
        else:
            objects = storage.all()

            key = "{}.{}".format(cmds[0], cmds[1])
            if key in objects:
                print(objects[key])
            else:
                print("** no instance found **")

    def do_destroy(self, arg):
        """
        Delete instance based on the class name and id.
        Usage: destroy <class_name> <id>
        """
        cmds = shlex.split(arg)

        if len(cmds) == 0:
            print("** class name missing **")
        elif cmds[0] not in self.valid_classes:
            print("** class doesn't exist **")
        elif len(cmds) < 2:
            print("** instance id missing **")
        else:
            objects = storage.all()
            key = "{}.{}".format(cmds[0], cmds[1])
            if key in objects:
                del objects[key]
                storage.save()
            else:
                print("** no instance found **")

    def do_all(self, arg):
        """
        Print the string representation of all instances or a specific class.
        Usage: <User>.all()
        """
        objects = storage.all()
        cmds = shlex.split(arg)

        if len(cmds) == 0:
            for key, value in objects.items():
                print(str(value))
        elif cmds[0] not in self.valid_classes:
            print("** class doesn't exist **")
        else:
            for key, value in objects.items():
                if key.split('.')[0] == cmds[0]:
                    print(str(value))

    def do_count(self, arg):
        """
        Counts number of instances of a class
        usage: <class name>.count()
        """
        cmds = shlex.split(arg)
        objects = storage.all()
        count = 0

        if arg:
            cls_nm = cmds[0]

        if cmds:
            if cls_nm in self.valid_classes:
                for obj in objects.values():
                    if obj.__class__.__name__ == cls_nm:
                        count += 1
                print(count)
            else:
                print("** invalid class name **")
        else:
            print("** class name missing **")

    def do_update(self, arg):
        """
        Update an instance by adding or updating an attribute.
        """
        cmds = shlex.split(arg)

        if len(cmds) == 0:
            print("** class name missing **")
        elif cmds[0] not in self.valid_classes:
            print("** class doesn't exist **")
        elif len(cmds) < 2:
            print("** instance id missing **")
        else:
            objects = storage.all()

            key = "{}.{}".format(cmds[0], cmds[1])
            if key not in objects:
                print("** no instance found **")
            elif len(cmds) < 3:
                print("** attribute name missing **")
            elif len(cmds) < 4:
                print("** value missing **")
            else:
                obj = objects[key]
                curly_braces = re.search(r"\{(.*?)\}", arg)

                if curly_braces:
                    try:
                        str_data = curly_braces.group(1)

                        arg_dict = ast.literal_eval("{" + str_data + "}")

                        attribute_names = list(arg_dict.keys())
                        attribute_values = list(arg_dict.values())
                        try:
                            attr_name1 = attribute_names[0]
                            attr_value1 = attribute_values[0]
                            setattr(obj, attr_name1, attr_value1)
                        except Exception:
                            pass
                        try:
                            attr_name2 = attribute_names[1]
                            attr_value2 = attribute_values[1]
                            setattr(obj, attr_name2, attr_value2)
                        except Exception:
                            pass
                    except Exception:
                        pass
                else:

                    attr_name = cmds[2]
                    attr_value = cmds[3]

                    try:
                        attr_value = eval(attr_value)
                    except Exception:
                        pass
                    setattr(obj, attr_name, attr_value)

                obj.save()


if __name__ == '__main__':
    HBNBCommand().cmdloop()