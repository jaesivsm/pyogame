#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
import time
from pyogame import tools, routines


def main(ctx, option):
    ctx.interface.login()
    ctx.interface.update_empire_state(ctx.empire)
    ctx.interface.crawl(ctx.empire)
    if option.rapatriate:
        routines.civil.rapatriate(ctx.interface, ctx.empire)
    if option.construct:
        routines.civil.in_place_empire_upgrade(ctx.interface, ctx.empire)
        routines.civil.resources_reception_and_construction(
                ctx.interface, ctx.empire)
        routines.civil.plan_construction(ctx.interface, ctx.empire)
    if option.probes:
        routines.guerrilla.check_neighborhood(
                [option.area_start, option.area_end],
                routines.guerrilla.SPY)
    if option.recycle:
        routines.guerrilla.check_neighborhood(
                [option.area_start, option.area_end],
                routines.guerrilla.RECYCLE)
    if not (option.rapatriate or option.construct or option.probes
            or option.recycle or option.idles or option.build):
        routines.civil.in_place_empire_upgrade(ctx.interface, ctx.empire)
        routines.civil.resources_reception_and_construction(
                ctx.interface, ctx.empire)
        routines.civil.rapatriate(ctx.interface, ctx.empire)
        routines.civil.plan_construction(ctx.interface, ctx.empire)
    ctx.interface.logout()


if __name__ == "__main__":
    args, logfile, loglevel = tools.parse_args()
    logger = tools.set_logger(logfile, args.user, loglevel)

    context = tools.get_context(args.user)

    if args.ui:
        if args.ui == 'overall':
            tools.ui.print_overall_status(context.empire)
        elif args.ui == 'toconstruct':
            tools.ui.print_to_construct(context.empire)
        elif args.ui == 'buildings':
            tools.ui.print_empire_buildings(context.empire)
        elif args.ui == 'technologies':
            tools.ui.print_technologies(context.empire)
        else:
            tools.ui.unknown_display(args.ui)

    elif args.build:
        plan = args.build.split('-')
        construct_name, level, planet_key = None, None, None
        if len(plan) == 2:
            construct_name, level = plan
        elif len(plan) == 3:
            construct_name, level, planet_key = plan
        level = int(level) if level else None
        if planet_key is not None:
            for planet in context.empire:
                if planet.key == planet_key:
                    planet.planner_add(construct_name, level)
        elif construct_name is not None and level is not None:
            context.empire.capital.planner_add(construct_name, level)
    elif args.tech:
        context.empire.planner_add(*args.tech.split('-'))

    elif not args.do_nothing:
        main(context, args)
    else:
        try:
            context.interface.login()
            context.interface.update_empire_state(context.empire)
            time.sleep(600)
        except KeyboardInterrupt:
            pass
    context.dump()

# vim: set et sts=4 sw=4 tw=120:
